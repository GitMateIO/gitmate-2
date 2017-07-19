import json

from django.conf import settings
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Comment import CommentType
from igitt_django.models import IGittComment
from igitt_django.models import IGittIssue
from igitt_django.models import IGittMergeRequest
from igitt_django.models import IGittRepository
from igitt_django.storage import get_object
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_hooks import ResponderRegistrar
from gitmate_hooks import signature_check


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
    repo_igitt_model = get_object(
        IGittRepository,
        token,
        full_name=gitmate_repo.full_name,
        hoster=Providers.GITHUB.value)
    options = gitmate_repo.get_plugin_settings()

    if event == 'issues':
        issue_data = webhook['issue']
        issue_igitt_model = get_object(
            IGittIssue,
            token,
            repo=repo_igitt_model,
            number=issue_data['number'])
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
        pr_data = webhook['pull_request']
        pr_igitt_model = get_object(
            IGittMergeRequest,
            token,
            repo=repo_igitt_model,
            number=pr_data['number'])
        pr = pr_igitt_model.to_igitt_instance(token)
        trigger_event = {
            'synchronize': MergeRequestActions.SYNCHRONIZED,
            'opened': MergeRequestActions.OPENED,
            'edited': MergeRequestActions.ATTRIBUTES_CHANGED
        }.get(webhook['action'])

        # no such webhook event action implemented yet
        if not trigger_event: # pragma: no cover
            raise NotImplementedError('Unrecognized action: '
                                      + event+ '/' + webhook['action'])

        ResponderRegistrar.respond(
            trigger_event, gitmate_repo, pr, options=options)

    elif event == 'issue_comment':
        kwargs = {
            'repo': repo_igitt_model,
            'type': CommentType.MERGE_REQUEST,
            'number':webhook['comment']['id']
        }
        if webhook['action'] != 'deleted':
            comment_igitt_model = get_object(IGittComment, token, **kwargs)
            comment = comment_igitt_model.to_igitt_instance(token)
            pr_igitt_model = get_object(
                IGittMergeRequest,
                token,
                repo=repo_igitt_model,
                number=webhook['issue']['number'])
            pr = pr_igitt_model.to_igitt_instance(token)
            trigger_event = MergeRequestActions.COMMENTED
            ResponderRegistrar.respond(
                trigger_event, gitmate_repo, pr, comment, options=options)
        else:
            try:
                IGittComment.objects.get(**kwargs).delete()
            except IGittComment.DoesNotExist:
                pass

    return Response(status=status.HTTP_200_OK)


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
    repo_data = (webhook['project'] if 'project' in webhook.keys()
                 else webhook['object_attributes']['target'])
    gitmate_repo = Repository.objects.filter(
        active=True,
        full_name=repo_data['path_with_namespace'],
        provider=Providers.GITLAB.value).first()
    raw_token = gitmate_repo.user.social_auth.get(
        provider=Providers.GITLAB.value).extra_data['access_token']
    token = Providers.GITLAB.get_token(raw_token)
    repo_igitt_model = get_object(
        IGittRepository,
        token,
        full_name=gitmate_repo.full_name,
        hoster=Providers.GITLAB.value)
    options = gitmate_repo.get_plugin_settings()

    if event == 'Issue Hook':
        issue_data = webhook['object_attributes']
        issue_igitt_model = get_object(
            IGittIssue, token, repo=repo_igitt_model, number=issue_data['iid'])
        issue = issue_igitt_model.to_igitt_instance(token)
        trigger_event = {
            'open': IssueActions.OPENED,
            'close': IssueActions.CLOSED,
            'reopen': IssueActions.REOPENED,
        }.get(issue_data['action'], IssueActions.ATTRIBUTES_CHANGED)

        ResponderRegistrar.respond(
            trigger_event, gitmate_repo, issue, options=options)

    elif event == 'Merge Request Hook':
        pr_data = webhook['object_attributes']
        pr_igitt_model = get_object(
            IGittMergeRequest, token,
            repo=repo_igitt_model, number=pr_data['iid'])
        pr = pr_igitt_model.to_igitt_instance(token)
        trigger_event = {
            'update': MergeRequestActions.ATTRIBUTES_CHANGED,
            'open': MergeRequestActions.OPENED,
            'reopen': MergeRequestActions.REOPENED,
        }.get(pr_data['action'])

        # nasty workaround for finding merge request resync
        if 'oldrev' in pr_data:
            trigger_event = MergeRequestActions.SYNCHRONIZED

        # no such webhook event action implemented yet
        if not trigger_event: # pragma: no cover
            raise NotImplementedError('Unrecgonized action: '
                                      + event+ '/' + pr_data['action'])

        ResponderRegistrar.respond(
            trigger_event, gitmate_repo, pr, options=options)

    elif event == 'Note Hook':
        comment_data = webhook['object_attributes']
        comment_type = {
            'MergeRequest': CommentType.MERGE_REQUEST,
            'Commit': CommentType.COMMIT,
            'Issue': CommentType.ISSUE,
            'Snippet': CommentType.SNIPPET
        }.get(comment_data['noteable_type'])

        if comment_type == CommentType.MERGE_REQUEST:
            pr_data = webhook['merge_request']
            pr_igitt_model = get_object(
                IGittMergeRequest, token,
                repo=repo_igitt_model, number=pr_data['iid'])
            pr = pr_igitt_model.to_igitt_instance(token)
            comment_igitt_model = get_object(
                IGittComment,
                token,
                type=comment_type,
                repo=repo_igitt_model,
                number=comment_data['id'],
                iid=pr_data['iid'])
            comment = comment_igitt_model.to_igitt_instance(token)
            trigger_event = MergeRequestActions.COMMENTED
            ResponderRegistrar.respond(
                trigger_event, gitmate_repo, pr, comment, options=options)

    return Response(status=status.HTTP_200_OK)
