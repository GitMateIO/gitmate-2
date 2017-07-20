import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Comment import CommentType
from igitt_django.models import IGittRepository
from igitt_django.models import IGittIssue
from igitt_django.storage import get_object_or_create
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
    webhook = json.loads(request.body.decode('utf-8'))

    event = request.META['HTTP_X_GITHUB_EVENT']
    repo_data = webhook['repository']

    gitmate_repo = Repository.objects.filter(
        active=True,
        full_name=repo_data['full_name'],
        provider=Providers.GITHUB.value).first()
    raw_token = gitmate_repo.user.social_auth.get(
        provider=Providers.GITHUB.value).extra_data['access_token']
    token = Providers.GITHUB.get_token(raw_token)
    repo_igitt_model, _ = get_object_or_create(
        IGittRepository,
        token,
        full_name=gitmate_repo.full_name,
        hoster=Providers.GITHUB.value)
    options = gitmate_repo.get_plugin_settings()

    if event == 'issues':
        issue_data = webhook['issue']
        issue_igitt_model, created = get_object_or_create(
            IGittIssue,
            token,
            repo=repo_igitt_model,
            number=issue_data['number'])
        if not created:
            issue_igitt_model.data = issue_data
            issue_igitt_model.save()
        issue = issue_igitt_model.to_igitt_instance(token)
        trigger_event = {
            'opened': IssueActions.OPENED,
            'closed': IssueActions.CLOSED,
            'reopened': IssueActions.REOPENED,
            'created': IssueActions.COMMENTED
        }.get(webhook['action'], IssueActions.ATTRIBUTES_CHANGED)

        ResponderRegistrar.respond(
            trigger_event, gitmate_repo, issue, options=options)

    elif event == 'pull_request':
        pull_request = webhook['pull_request']
        pull_request_obj = GitHubMergeRequest(
            token, repo_data['full_name'], pull_request['number'])
        trigger_event = {
            'synchronize': MergeRequestActions.SYNCHRONIZED,
            'opened': MergeRequestActions.OPENED,
            'edited': MergeRequestActions.ATTRIBUTES_CHANGED
        }.get(webhook['action'])

        # no such webhook event action implemented yet
        if not trigger_event: # pragma: no cover
            raise NotImplementedError('Unrecgonized action: '
                                      + event+ '/' + webhook['action'])
        ResponderRegistrar.respond(
            trigger_event, gitmate_repo, pull_request_obj, options=options)

    elif event == 'issue_comment':
        if webhook['action'] != 'deleted':
            comment = webhook['comment']
            pull_request_obj = GitHubMergeRequest(
                token,
                repo_data['full_name'],
                webhook['issue']['number'])
            comment_obj = GitHubComment(
                token,
                repo_data['full_name'],
                CommentType.MERGE_REQUEST,
                comment['id'])
            ResponderRegistrar.respond(
                MergeRequestActions.COMMENTED,
                gitmate_repo,
                pull_request_obj,
                comment_obj,
                options=options)

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
    event = request.META['HTTP_X_GITLAB_EVENT']
    repository = (webhook['project'] if 'project' in webhook.keys()
                  else webhook['object_attributes']['target'])
    repo_obj = Repository.objects.filter(
        active=True,
        full_name=repository['path_with_namespace'],
        provider=Providers.GITLAB.value).first()
    raw_token = repo_obj.user.social_auth.get(
        provider=Providers.GITLAB.value).extra_data['access_token']
    token = GitLabOAuthToken(raw_token)

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
        ipull_request = GitLabMergeRequest(
            token, repository['path_with_namespace'], pull_request['iid'])
        trigger_event = {
            'update': MergeRequestActions.ATTRIBUTES_CHANGED,
            'open': MergeRequestActions.OPENED,
            'reopen': MergeRequestActions.REOPENED,
        }.get(pull_request['action'])

        # nasty workaround for finding merge request resync
        if 'oldrev' in pull_request:
            trigger_event = MergeRequestActions.SYNCHRONIZED

        # no such webhook event action implemented yet
        if not trigger_event: # pragma: no cover
            raise NotImplementedError('Unrecgonized action: '
                                      + event+ '/' + pull_request['action'])

        ResponderRegistrar.respond(
            trigger_event, repo_obj, ipull_request,
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
