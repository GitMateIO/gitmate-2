import json

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLab import GitLab
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Actions import PipelineActions
from IGitt.Interfaces.Comment import CommentType

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_hooks.utils import ResponderRegistrar
from gitmate_hooks.utils import signature_check


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
    repository = webhook_data['repository']['full_name']

    repo_obj = get_object_or_404(Repository,
                                 active=True,
                                 full_name=repository,
                                 provider=Providers.GITHUB.value)

    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITHUB.value).extra_data['access_token']

    try:
        action, objs = GitHub(GitHubToken(raw_token)).handle_webhook(
            repository, request.META['HTTP_X_GITHUB_EVENT'], webhook_data)
    except NotImplementedError:  # pragma: no cover
        # IGitt can't handle it yet, upstream issue, no plugin needs it yet
        return Response(status=status.HTTP_200_OK)

    ResponderRegistrar.respond(action, repo_obj, *objs)

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

    def _get_repo_name(data: dict):
        # Push, Tag, Issue, Note, Wiki Page and Pipeline Hooks
        if 'project' in data.keys():
            return data['project']['path_with_namespace']

        # Merge Request Hook
        if 'object_attributes' in data.keys():
            return data['object_attributes']['target']['path_with_namespace']

        # Build Hook
        if 'repository' in data.keys():
            ssh_url = data['repository']['git_ssh_url']
            return ssh_url[ssh_url.find(':') + 1: ssh_url.rfind('.git')]

    repository = _get_repo_name(webhook)

    repo_obj = get_object_or_404(Repository,
                                 active=True,
                                 full_name=repository,
                                 provider=Providers.GITLAB.value)

    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITLAB.value).extra_data['access_token']

    try:
        action, objs = GitLab(GitLabOAuthToken(raw_token)).handle_webhook(
            repository, request.META['HTTP_X_GITLAB_EVENT'], webhook)
    except NotImplementedError:  # pragma: no cover
        # IGitt can't handle it yet, upstream issue, no plugin needs it yet
        return Response(status=status.HTTP_200_OK)

    ResponderRegistrar.respond(action, repo_obj, *objs)

    return Response(status=status.HTTP_200_OK)
