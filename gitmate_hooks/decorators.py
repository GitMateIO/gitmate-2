from enum import Enum
from functools import wraps
from hashlib import sha1
from typing import Callable
import hmac
import re

from celery.utils.log import get_logger
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Comment import Comment
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from gitmate_config import Providers


COMMENT_FOOTER_REGEX = re.compile(
    r'\(Powered by \[GitMate\.io\]\(https:\/\/gitmate\.io\)\)')


def block_comment(func):
    """
    Block events when the comment contains a timestamp signature.
    """

    @wraps(func)
    def wrapped(klass, event: Enum, *args, **kwargs):
        if event in [MergeRequestActions.COMMENTED, IssueActions.COMMENTED]:
            comment = args[1]
            assert issubclass(comment.__class__, Comment)
            if COMMENT_FOOTER_REGEX.search(comment.body):
                return []
        return func(klass, event, *args, **kwargs)
    return wrapped


def signature_check(key: str,
                    provider: str,
                    http_header_name: str):
    """
    Decorator for views that checks if the signature from request header
    matches the one registered for webhooks.

    :param key:                 The client key used to verify the hash.
    :param provider:            The provider for which hash is to be verified.
    :param http_header_name:    Name of HTTP request header which contains the
                                secure signature.
    :return:                    The response generated from the view.
    """
    def decorator(view: Callable):

        @wraps(view)
        def _view_wrapper(request: Request, *args, **kwargs):

            # key not found, verification turned off!
            if not key:
                logger = get_logger('celery.worker')
                logger.warning('Webhook signature verification turned off!'
                               'Please verify WEBHOOK_SECRET in settings.')
                return view(request, *args, **kwargs)

            # improper request structure
            if not all([http_header_name in request.META, len(request.body)]):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if provider == Providers.GITHUB.value:
                hashed = hmac.new(key.encode('utf-8'), request.body, sha1)
                generated_signature = hashed.hexdigest()
                sign = request.META[http_header_name]

                if generated_signature == sign[5:]:
                    return view(request, *args, **kwargs)

            elif provider == Providers.GITLAB.value:
                if request.META[http_header_name] == key:
                    return view(request, *args, **kwargs)

            # signature does not match
            return Response(status=status.HTTP_403_FORBIDDEN)

        return _view_wrapper
    return decorator
