from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from IGitt.GitHub.GitHub import GitHub
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class UserDetailsView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        return Response(UserSerializer(request.user).data)


class UserOwnedRepositoriesView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            provider = request.query_params['provider']
            provider_data = request.user.social_auth.get(
                provider=provider).extra_data
            access_token = provider_data['access_token']
            if provider == 'github':
                host = GitHub(access_token)
            else:
                raise NotImplementedError
            content = {
                'owned': host.owned_repositories,
                'write': host.write_repositories
            }
        except (MultiValueDictKeyError, ObjectDoesNotExist):
            content = {
                'error': 'Requires a valid provider name',
                'status_code': 500
            }
        except NotImplementedError:
            content = {
                'error': 'Plugin for host not yet developed',
                'status_code': 500
            }
        except RuntimeError:
            content = {
                'error': 'Bad credentials',
                'status_code': 401
            }
        return Response(content)
