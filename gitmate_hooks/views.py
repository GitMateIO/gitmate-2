import json

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from IGitt.GitHub.GitHub import GitHub
from IGitt.GitLab.GitLab import GitLab

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_config.models import Installation
from gitmate_hooks.utils import ResponderRegistrar
from gitmate_hooks.decorators import signature_check


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

    # responding to regular webhook calls for registered events
    if 'repository' in webhook:
        repository = webhook['repository']
        repo_obj = get_object_or_404(Repository,
                                     (Q(identifier=repository['id']) |
                                      Q(full_name=repository['full_name'])),
                                     active=True,
                                     provider=Providers.GITHUB.value)
        token = repo_obj.token

    # webhook was received from an installation
    if 'installation' in webhook:
        installation_obj, _ = Installation.objects.get_or_create(
            provider=Providers.GITHUB.value,
            identifier=webhook['installation']['id'])
        token = installation_obj.token

    try:
        for action, objs in GitHub(token).handle_webhook(event, webhook):
            ResponderRegistrar.respond(action, *objs, repo=repo_obj)
    except NotImplementedError:  # pragma: no cover
        # IGitt can't handle it yet, upstream issue, no plugin needs it yet
        return Response(status=status.HTTP_200_OK)

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

    try:
        for action, objs in GitLab(repo_obj.token).handle_webhook(
                event, webhook):
            ResponderRegistrar.respond(action, *objs, repo=repo_obj)
    except NotImplementedError:  # pragma: no cover
        # IGitt can't handle it yet, upstream issue, no plugin needs it yet
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_200_OK)
