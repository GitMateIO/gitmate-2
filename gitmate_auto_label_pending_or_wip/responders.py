from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(MergeRequestActions.SYNCHRONIZED)
def mark_pending_review_or_wip_accordingly(
    pr: MergeRequest,
    wip_label: str='Work in progress',
    pending_review_label: str='Review pending'
):
    """
    Labels the pull request as pending review and removes work in
    progress on every changed PR accordingly. But retains work in progress
    label, if title of the pull request begins with "wip".
    """
    labels = pr.issue.labels
    if not pr.issue.title.lower().startswith('wip'):
        labels.add(pending_review_label)
        labels.discard(wip_label)
    else:
        labels.add(wip_label)
        labels.discard(pending_review_label)

    pr.issue.labels = labels