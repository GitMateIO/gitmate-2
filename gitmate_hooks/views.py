import json

from IGitt.GitHub.GitHub import GitHub
from IGitt.GitLab.GitLab import GitLab
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Actions import PipelineActions
from IGitt.Interfaces.Comment import CommentType
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_hooks import ResponderRegistrar
from gitmate_hooks import signature_check


@csrf_exempt
@api_view(['POST'])
@signature_check(settings.WEBHOOK_SECRET,
                 Providers.GITHUB.value,
                 'HTTP_X_HUB_SIGNATURE')
def github_webhook_receiver(request):
    """
    Receives webhooks from GitHub and carries out the approriate action.
    """
    webhook_data = json.loads(request.body.decode('utf-8'))

    repository = webhook_data['repository']

    repo_obj = Repository.objects.filter(
        active=True,
        full_name=repository['full_name'],
        provider=Providers.GITHUB.value).first()
    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITHUB.value).extra_data['access_token']

    action, objs = GitHub(GitHubToken(raw_token)).handle_webhook(
        request.META['HTTP_X_GITHUB_EVENT'], webhook_data)

    ResponderRegistrar.respond(action, repo_obj, *objs,
                               options=repo_obj.get_plugin_settings())

    return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@signature_check(settings.WEBHOOK_SECRET,
                 Providers.GITLAB.value,
                 'HTTP_X_GITLAB_TOKEN')
def gitlab_webhook_receiver(request):
    """
    Receives webhooks from GitLab and carries out the appropriate action.
    """
    webhook = json.loads(request.body.decode('utf-8'))
    repository = (webhook['project'] if 'project' in webhook.keys()
                  else webhook['object_attributes']['target'])
    repo_obj = Repository.objects.filter(
        active=True,
        full_name=repository['path_with_namespace'],
        provider=Providers.GITLAB.value).first()
    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITLAB.value).extra_data['access_token']

    action, objs = GitLab(GitLabOAuthToken(raw_token)).handle_webhook(
        request.META['HTTP_X_GITLAB_EVENT'], webhook)

    ResponderRegistrar.respond(action, repo_obj, *objs,
                               options=repo_obj.get_plugin_settings())

    return Response(status=status.HTTP_200_OK)
