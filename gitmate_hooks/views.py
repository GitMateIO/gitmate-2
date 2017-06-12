import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
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
@signature_check(settings.GITHUB_WEBHOOK_SECRET, 'HTTP_X_HUB_SIGNATURE')
def github_webhook_receiver(request):
    """
    Receives webhooks from GitHub and carries out the approriate action.
    """
    webhook_data = json.loads(request.body.decode('utf-8'))

    event = request.META['HTTP_X_GITHUB_EVENT']
    repository = webhook_data['repository']

    repo_obj = Repository.objects.filter(
        active=True,
        full_name=repository['full_name'],
        provider=Providers.GITHUB.value).first()
    token = repo_obj.user.social_auth.get(
        provider=Providers.GITHUB.value).extra_data['access_token']

    if event == 'issues':
        issue = webhook_data['issue']
        issue_obj = GitHubIssue(
            token, repository['full_name'], issue['number'])
        trigger_event = {
            'opened': IssueActions.OPENED,
            'closed': IssueActions.CLOSED,
            'reopened': IssueActions.REOPENED,
            'created': IssueActions.COMMENTED
        }.get(webhook_data['action'], IssueActions.ATTRIBUTES_CHANGED)

        ResponderRegistrar.respond(
            trigger_event, repo_obj, issue_obj,
            options=repo_obj.get_plugin_settings())

    elif event == 'pull_request':
        pull_request = webhook_data['pull_request']

        if webhook_data['action'] in ['synchronize', 'opened']:
            pull_request_obj = GitHubMergeRequest(
                token, repository['full_name'], pull_request['number'])
            ResponderRegistrar.respond(
                MergeRequestActions.SYNCHRONIZED, repo_obj, pull_request_obj,
                options=repo_obj.get_plugin_settings())

            if webhook_data['action'] == 'opened':
                ResponderRegistrar.respond(
                    MergeRequestActions.OPENED, repo_obj, pull_request_obj,
                    options=repo_obj.get_plugin_settings())

    elif event == 'issue_comment':
        if webhook_data['action'] != 'deleted':
            comment = webhook_data['comment']
            pull_request_obj = GitHubMergeRequest(
                    token,
                    repository['full_name'],
                    webhook_data['issue']['number'])
            comment_obj = GitHubComment(
                    token,
                    repository['full_name'],
                    CommentType.MERGE_REQUEST,
                    comment['id'])
            ResponderRegistrar.respond(
                    MergeRequestActions.COMMENTED,
                    repo_obj,
                    pull_request_obj,
                    comment_obj,
                    options=repo_obj.get_plugin_settings())

    return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def gitlab_webhook_receiver(request):
    """
    Receives webhooks from GitLab and carries out the appropriate action.
    """
    webhook = json.loads(request.body.decode('utf-8'))
    event = request.META['HTTP_X_GITLAB_EVENT']
    repository = (webhook['project'] if 'project' in webhook.keys()
                  else webhook['object_attributes']['target'])
    repo_obj = Repository.objects.filter(
        active=True,
        full_name=repository['path_with_namespace'],
        provider=Providers.GITLAB.value).first()
    token = repo_obj.user.social_auth.get(
        provider=Providers.GITLAB.value).extra_data['access_token']

    if event == 'Issue Hook':
        issue = webhook['object_attributes']
        issue_obj = GitLabIssue(
            token, repository['path_with_namespace'], issue['iid'])
        trigger_event = {
            'open': IssueActions.OPENED,
            'close': IssueActions.CLOSED,
            'reopen': IssueActions.REOPENED,
        }.get(issue['action'], IssueActions.ATTRIBUTES_CHANGED)

        ResponderRegistrar.respond(
            trigger_event, repo_obj, issue_obj,
            options=repo_obj.get_plugin_settings())

    elif event == 'Merge Request Hook':
        pull_request = webhook['object_attributes']
        if pull_request['action'] in ['update', 'open', 'reopen']:
            ipull_request = GitLabMergeRequest(
                token, repository['path_with_namespace'], pull_request['iid'])
            ResponderRegistrar.respond(
                MergeRequestActions.SYNCHRONIZED, repo_obj, ipull_request,
                options=repo_obj.get_plugin_settings())

            if pull_request['action'] == 'open':
                ResponderRegistrar.respond(
                    MergeRequestActions.OPENED, repo_obj, ipull_request,
                    options=repo_obj.get_plugin_settings())

    elif event == 'Note Hook':
        comment = webhook['object_attributes']
        comment_type = {
            'MergeRequest': CommentType.MERGE_REQUEST,
            'Commit': CommentType.COMMIT,
            'Issue': CommentType.ISSUE,
            'Snippet': CommentType.SNIPPET
        }.get(comment['noteable_type'])

        if comment_type == CommentType.MERGE_REQUEST:
            mr = webhook['merge_request']
            igitt_mr = GitLabMergeRequest(
                token,
                repository['path_with_namespace'],
                mr['iid'])
            igitt_comment = GitLabComment(
                token,
                repository['path_with_namespace'],
                mr['iid'],
                comment_type,
                comment['id'])
            ResponderRegistrar.respond(
                MergeRequestActions.COMMENTED,
                repo_obj,
                igitt_mr,
                igitt_comment,
                options=repo_obj.get_plugin_settings())

    return Response(status=status.HTTP_200_OK)
