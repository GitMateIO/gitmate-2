from collections import defaultdict

from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_config.models import Repository
from gitmate.utils import lock_igitt_object
from gitmate_hooks.utils import ResponderRegistrar
from .models import MergeRequestModel


@ResponderRegistrar.responder(
    'issue_pr_sync',
    MergeRequestActions.OPENED,
    MergeRequestActions.REOPENED,
    MergeRequestActions.SYNCHRONIZED
)
def sync_updated_pr_with_issue(pr: MergeRequest,
                               sync_assignees: bool='Synchronize Assignees'):
    issues = pr.closes_issues
    repo = Repository.from_igitt_repo(pr.repository)
    pr_obj = MergeRequestModel.objects.get_or_create(
        repo=repo, number=pr.number)[0]
    data = defaultdict(dict)

    with lock_igitt_object('label mr', pr):
        labels = pr.labels
        for issue in issues:
            labels = issue.labels | labels
        pr.labels = labels

    if sync_assignees:
        with lock_igitt_object('assign mr', pr):
            assignees = pr.assignees
            for issue in issues:
                assignees |= issue.assignees
                data[str(issue.number)]['assignees'] = True
            pr.assignees = assignees

    pr_obj.closes_issues = data
    pr_obj.save()


@ResponderRegistrar.responder('issue_pr_sync', IssueActions.LABELED)
def sync_label_add_from_issue_with_pr(issue: Issue, label: str):
    for pr_object in MergeRequestModel.find_mrs_with_issue(issue):
        pr = pr_object.igitt_pr
        with lock_igitt_object('label mr', pr):
            pr.labels |= {label}


@ResponderRegistrar.responder('issue_pr_sync', IssueActions.UNLABELED)
def sync_label_remove_from_issue_with_pr(issue: Issue, label: str):
    for pr_object in MergeRequestModel.find_mrs_with_issue(issue):
        pr = pr_object.igitt_pr
        with lock_igitt_object('label mr', pr):
            pr.labels -= {label}


@ResponderRegistrar.responder(
    'issue_pr_sync',
    IssueActions.REOPENED,
    IssueActions.ATTRIBUTES_CHANGED
)
def sync_pr_with_updated_issue(issue: Issue,
                               sync_assignees: bool='Synchronize Assignees'):

    if not sync_assignees:  # pragma: no cover
        return

    for pr_object in MergeRequestModel.find_mrs_with_issue(issue):
        pr = pr_object.igitt_pr
        with lock_igitt_object('assign mr', pr):
            pr.assignees |= issue.assignees
        pr_object.closes_issues.update({str(issue.number): True})
        pr_object.save()


@ResponderRegistrar.responder('issue_pr_sync',
                              MergeRequestActions.CLOSED)
def remove_merge_requests(pr: MergeRequest):
    """
    Remove closed and merged MRs from database.
    """
    repo = Repository.from_igitt_repo(pr.repository)
    try:
        MergeRequestModel.objects.get(repo=repo, number=pr.number).delete()
    except MergeRequestModel.DoesNotExist:  # pragma: no cover
        # Merge request doesn't exist in db. Maybe it wasn't synchronized after
        # gitmate was enabled.
        pass
