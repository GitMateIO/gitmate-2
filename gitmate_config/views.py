from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitLab.GitLab import GitLab
from rest_framework import mixins
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Organization
from gitmate_config.models import Repository

from .serializers import PluginSettingsSerializer
from .serializers import RepositorySerializer
from .serializers import UserSerializer
from .utils import divert_access_to_orgs
from .utils import divert_access_to_repos


class RepositoryViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """
    Retrieves repositories this user has access to.
    """
    serializer_class = RepositorySerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Repository.objects.filter(
            admins__in=[self.request.user]
        ).order_by('-active', 'full_name')

    def list(self, request):
        if int(request.GET.get('cached', '1')) > 0:
            return super().list(request)

        # Update db model
        hoster = {
            Providers.GITHUB.value: GitHub,
            Providers.GITLAB.value: GitLab,
        }

        for provider in Providers:
            try:
                raw_token = self.request.user.social_auth.get(
                    provider=provider.value
                ).extra_data['access_token']

                # Orgs already checked for master access of the current user
                checked_orgs = set()

                master_repos = hoster[provider.value](
                    provider.get_token(raw_token)).master_repositories
                repo_ids = [repo.identifier for repo in master_repos]
                repo_names = [repo.full_name for repo in master_repos]

                for igitt_repo in master_repos:
                    repo, _ = Repository.objects.filter(
                        Q(identifier=igitt_repo.identifier) |
                        Q(full_name=igitt_repo.full_name)
                    ).get_or_create(
                        provider=provider.value,
                        defaults={'active': False,
                                  'user': request.user,
                                  'full_name': igitt_repo.full_name,
                                  'identifier': igitt_repo.identifier})
                    repo.admins.add(request.user)

                    if repo.org is None:
                        igitt_org = igitt_repo.top_level_org

                        org, created = Organization.objects.get_or_create(
                            name=igitt_org.name,
                            provider=provider.value,
                            defaults={'primary_user': request.user})

                        if created or (
                            org.name not in checked_orgs
                            and request.user not in org.admins.all()
                        ):
                            masters = {m.identifier for m in igitt_org.masters}
                            for admin in repo.admins.all():
                                if admin.social_auth.get(
                                        provider=repo.provider
                                ).extra_data['id'] in masters:
                                    org.admins.add(admin)

                            if created:
                                # The user who first lists a repo will also be
                                # able to manage the org as he's the only one
                                org.admins.add(request.user)
                                org.save()

                            checked_orgs.add(org.name)

                    repo.save()

                # unlink the repositories in the current provider for which the
                # user no longer has access to
                inaccessible_repos = self.get_queryset().filter(
                    provider=provider.value).exclude(
                        Q(identifier__in=repo_ids) |
                        Q(full_name__in=repo_names))

                assert all([repo.full_name not in repo_names
                            for repo in inaccessible_repos])
                assert all([repo.user == request.user
                            for repo in inaccessible_repos])
                assert all([request.user in repo.admins.all()
                            for repo in inaccessible_repos])

                # delete them if he's the only administrator
                inaccessible_repos.annotate(
                    num_admins=Count('admins')
                ).filter(num_admins=1).delete()

                # give the access to someone else otherwise
                divert_access_to_repos(inaccessible_repos, request.user)

                # TODO: validate if a cached repo was removed. Handling if it
                # was active?
            except UserSocialAuth.DoesNotExist: # pragma: no cover
                pass  # User never gave us his key for that provider

        return super().list(request)

    def update(self, request, *args, **kwargs):
        """
        Updates the repository. This will be called by `super` on both
        partial and full update (PATCH and PUT), only the `active` property
        is writable (see serializer) so this takes care of
        activation/decativation of the webhook only.
        """
        instance = self.get_object()
        active_changed = (request.data['active'] != instance.active
                          if 'active' in request.data
                          else False)

        retval = super().update(request, *args, **kwargs)

        if active_changed:
            instance = self.get_object()
            repo = instance.igitt_repo
            hook_url = 'https://{domain}/webhooks/{provider}'.format(
                domain=settings.HOOK_DOMAIN, provider=instance.provider)

            if instance.active:
                # increment the repository activation count
                instance.activation_count += 1
                instance.save()

                # turn on default plugins for the first time only
                if instance.activation_count == 1:
                    plugins = [{'name': plugin.name, 'active': True}
                               for plugin in Plugin.get_default_list()]
                    instance.set_plugin_settings(plugins)

                # register the webhook for repository events
                repo.register_hook(hook_url, settings.WEBHOOK_SECRET)
            else:
                repo.delete_hook(hook_url)

        return retval


class UserViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin
):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        if self.kwargs.get('pk') in ['me', self.request.user.pk]:
            return self.request.user
        raise PermissionDenied

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        # Scan for user repos. If they have multiple admins, make someone else
        # the operating user and then remove the user.
        divert_access_to_repos(user.repository_set.all(), user)

        # Scan for user maintained orgs. If they have multiple admins, make
        # someone else the maintainer and then remove the user.
        divert_access_to_orgs(user.orgs.all(), user)

        return super().destroy(request, *args, **kwargs)


class PluginSettingsViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin
):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = PluginSettingsSerializer

    def get_queryset(self):
        return [repo.get_plugin_settings_with_info(self.request)
                for repo in Repository.objects.filter(user=self.request.user)]

    def retrieve(self, request, pk=None):
        repo = get_object_or_404(Repository, pk=pk)
        serializer = PluginSettingsSerializer(
            instance=repo.get_plugin_settings_with_info(request))
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        repo = get_object_or_404(Repository, pk=pk)
        repo.set_plugin_settings(request.data)
        serializer = PluginSettingsSerializer(
            instance=repo.get_plugin_settings_with_info(request))
        return Response(serializer.data, status=status.HTTP_200_OK)
