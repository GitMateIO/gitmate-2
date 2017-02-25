from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitHub.GitHubRepository import GitHubRepository
from rest_framework import mixins
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from gitmate_config import Providers
from gitmate_config.models import Plugin
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
        return Repository.objects.filter(user=self.request.user)

    def list(self, request):
        # Update db model
        for provider in Providers:
            try:
                token = self.request.user.social_auth.get(
                    provider=provider.value
                ).extra_data['access_token']
                for repo in GitHub(token).owned_repositories:
                    try:
                        Repository.objects.get(
                            provider=provider.value, full_name=repo)

                    except Repository.DoesNotExist:  # New repo found!
                        Repository(
                            active=False, user=request.user,
                            provider=provider.value, full_name=repo
                        ).save()

                # TODO: validate if a cached repo was removed. Handling if it
                # was active?
            except:
                continue

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
        hook_url = "https://" + request.META['HTTP_HOST'] + "/webhooks/github"
        if instance.active:
            repo.register_hook(hook_url, settings.GITHUB_WEBHOOK_SECRET)
        else:
            repo.delete_hook(hook_url)

        return retval


class UserDetailsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        return Response(UserSerializer(request.user).data, status.HTTP_200_OK)


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
        return Plugin.get_all_settings_by_user(self.request.user)

    def retrieve(self, request, pk=None):
        repo = get_object_or_404(Repository, pk=pk)
        serializer = PluginSettingsSerializer(
            instance=Plugin.get_all_settings_by_repo(repo))
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        repo = get_object_or_404(Repository, pk=pk)
        Plugin.set_all_settings_for_repo(repo, request.data)
        return Response(status=status.HTTP_200_OK)
