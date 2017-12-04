from functools import wraps
from typing import Union

from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks.utils import ResponderRegistrar


def verify_comment_author_permission(min_access: AccessLevel):
    """
    Decorator for responders that checks if the comment author has an access
    level greater than or equal to the minimum access level specified.

    :param min_access:   Minimum access level required.
    """
    def decorator(responder: ResponderRegistrar.responder):

        @wraps(responder)
        def _wrapper(
                obj: Union[MergeRequest, Issue],
                cmt: Comment,
                *args, **kwargs):

            author_access = obj.repository.get_permission_level(cmt.author)
            if author_access.value >= min_access.value:
                return responder(obj, cmt, *args, **kwargs)
            else:
                msg = ('Sorry @{}, you do not have the necessary permission '
                       'levels to perform the action.'.format(
                           cmt.author.username))
                obj.add_comment(msg)

        return _wrapper
    return decorator
