from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(
    'issue_pr_sync',
    MergeRequestActions.OPENED,
    MergeRequestActions.SYNCHRONIZED
)
def sync_issues_with_merge_requests(pr: MergeRequest):
    for issue in pr.closes_issues:
        # sync merge request labels with those of the referenced issue
        with lock_igitt_object('label mr', pr):
            pr.labels = issue.labels.union(pr.labels)

        # assign the pull request to the same assignee as the referenced issue
        with lock_igitt_object('assign mr', pr):
            for assignee in issue.assignees:
                pr.assign(assignee)
