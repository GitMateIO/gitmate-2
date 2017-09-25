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

    repo_obj = get_object_or_404(Repository,
                                 active=True,
                                 full_name=repository['full_name'],
                                 provider=Providers.GITHUB.value)

    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITHUB.value).extra_data['access_token']

    try:
        action, objs = GitHub(GitHubToken(raw_token)).handle_webhook(
            request.META['HTTP_X_GITHUB_EVENT'], webhook_data)
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
    repository = (
        webhook['project_name'].replace(' / ', '/')
        if 'project_name' in webhook.keys()
        else webhook['project']['path_with_namespace']
        if 'project' in webhook.keys()
        else webhook['object_attributes']['target']['path_with_namespace']
    )

    repo_obj = get_object_or_404(Repository,
                                 active=True,
                                 full_name=repository,
                                 provider=Providers.GITLAB.value)

    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITLAB.value).extra_data['access_token']

    try:
        action, objs = GitLab(GitLabOAuthToken(raw_token)).handle_webhook(
            request.META['HTTP_X_GITLAB_EVENT'], webhook)
    except NotImplementedError:  # pragma: no cover
        # IGitt can't handle it yet, upstream issue, no plugin needs it yet
        return Response(status=status.HTTP_200_OK)

    ResponderRegistrar.respond(action, repo_obj, *objs)

    return Response(status=status.HTTP_200_OK)
