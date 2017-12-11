from IGitt.Interfaces.Actions import MergeRequestActions, IssueActions
from IGitt.Interfaces.MergeRequest import MergeRequest


from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.responder(
    'unassign',
    MergeRequestActions.OPENED,
    MergeRequestActions.SYNCHRONIZED,
)
def gitmate_unassign_sync(pr: MergeRequest):
    pr.add_comment('Hello World!')


@ResponderRegistrar.responder(
    'unassign',
    IssueActions.COMMENTED,
    IssueActions.ATTRIBUTES_CHANGED,
)