from django.core.signing import TimestampSigner
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.responder('welcome_commenter', MergeRequestActions.OPENED)
def add_welcome_comment(
    pr: MergeRequest,
    autorespond_text: str='Hi! This is GitMate v2.0!'
):
    """
    Adds a welcome comment to pull requests.
    """
    sign = TimestampSigner().sign(autorespond_text)
    msg = ("{}\n\nThis message was posted by [GitMate.io](https://gitmate.io)"
           " with timestamp signature `{}`".format(autorespond_text, sign))
    pr.add_comment(msg)
