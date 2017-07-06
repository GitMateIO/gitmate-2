from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder('welcome_commenter', MergeRequestActions.OPENED)
def add_welcome_comment(
    pr: MergeRequest,
    autorespond_text: str='Hi! This is GitMate v2.0!'
):
    """
    Adds a welcome comment to pull requests.
    """
    pr.add_comment(autorespond_text)
