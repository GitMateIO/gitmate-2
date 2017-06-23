from django.conf import settings
from django.contrib.auth.models import User
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
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Repository

from .serializers import PluginSettingsSerializer
from .serializers import RepositorySerializer
from .serializers import UserSerializer


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

                for repo in hoster[provider.value](
                        provider.get_token(raw_token)).master_repositories:
                    try:
                        # some user already created this
                        irepo = Repository.objects.get(
                            provider=provider.value, full_name=repo.full_name)
                    except Repository.DoesNotExist:
                        # Newly created
                        irepo = Repository(
                            active=False, user=request.user,
                            provider=provider.value, full_name=repo.full_name)
                        irepo.save()
                    finally:
                        # add the current users as an admin user since he
                        # can write to it too. Also, django doesn't add it
                        # again if it's already there.
                        irepo.admins.add(request.user)
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
        retval = super().update(request, *args, **kwargs)

        instance = self.get_object()
        repo = instance.igitt_repo()
        hook_url = 'https://{domain}/webhooks/{provider}'.format(
            domain = settings.HOOK_DOMAIN, provider=instance.provider)

        if instance.active:
            repo.register_hook(hook_url, settings.WEBHOOK_SECRET)
        else:
            repo.delete_hook(hook_url)

        return retval

class UserViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        if self.kwargs.get('pk') in ['me', self.request.user.pk]:
            return self.request.user
        raise PermissionDenied

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
