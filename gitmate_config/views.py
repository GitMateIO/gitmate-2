from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitHub.GitHubRepository import GitHubRepository
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Repository

from .serializers import RepositorySerializer
from .serializers import UserSerializer


class UserDetailsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        return Response(UserSerializer(request.user).data, status.HTTP_200_OK)


class UserOwnedRepositoriesView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {}
        status_code = status.HTTP_200_OK
        for provider in Providers:
            try:
                provider_data = request.user.social_auth.get(
                    provider=provider.value).extra_data
                access_token = provider_data['access_token']
                host = GitHub(access_token)
                content.update({provider.value: host.owned_repositories})
            except RuntimeError:
                content = {'error': 'Bad credentials'}
                status_code = status.HTTP_401_UNAUTHORIZED
            return Response(content, status_code)


class ActivateRepositoryView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        received_json = request.data
        try:
            provider = received_json['provider'].lower()
            repo_name = received_json['repository']
            if provider == Providers.GITHUB.value:
                token = request.user.social_auth.get(
                    provider=provider).extra_data['access_token']
                repo = GitHubRepository(token, repo_name)
                repo_obj = Repository(
                    active=True, user=request.user,
                    provider=provider, full_name=repo_name)
                repo_obj.save()
                repo.register_hook(request.scheme + "://" +
                                   request.META['HTTP_HOST'] +
                                   "/webhooks/github")
                return Response(RepositorySerializer(repo_obj).data,
                                status.HTTP_201_CREATED)
            else:
                raise NotImplementedError
        except (KeyError, NotImplementedError):
            return Response({'error': "Invalid request"},
                            status.HTTP_400_BAD_REQUEST)
        except RuntimeError:
            return Response({'error': "Bad credentials"},
                            status.HTTP_401_UNAUTHORIZED)


class PluginSettingsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            provider = request.query_params['provider']
            name = request.query_params['repo']
            repo = Repository.objects.get(full_name=name, provider=provider)
            content = Plugin.get_all_settings_detailed(repo)
            return Response(content, status.HTTP_200_OK)
        except MultiValueDictKeyError:
            content = {'error': 'Requires valid provider and repo names.'}
            return Response(content, status.HTTP_400_BAD_REQUEST)
        except Repository.DoesNotExist:
            content = {'error': 'No such repository exists.'}
            return Response(content, status.HTTP_404_NOT_FOUND)
