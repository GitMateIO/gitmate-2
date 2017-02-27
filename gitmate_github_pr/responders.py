from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(MergeRequestActions.OPENED)
def respond_to_github_pull_request(
    pr: MergeRequest,
    autorespond_active: bool=True,
    autorespond_text: str="Hi! This is GitMate v2.0!"
):
    """
    Responds to GitHub Pull Requests.
    """
    if not autorespond_active:
        return

    pr.issue.add_comment(autorespond_text)
