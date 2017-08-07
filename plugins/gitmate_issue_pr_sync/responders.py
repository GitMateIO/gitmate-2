from collections import defaultdict

from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(
    'issue_pr_sync',
    MergeRequestActions.OPENED,
    MergeRequestActions.SYNCHRONIZED
)
def sync_updated_pr_with_issue(pr: MergeRequest,
                               sync_assignees: bool='Synchronize Assignees'):
    # Don't move to module code! Apps aren't loaded yet.
    from gitmate_config.models import Repository
    from .models import MergeRequestModel

    issues = pr.closes_issues
    repo = Repository.from_igitt_repo(pr.repository)
    pr_obj = MergeRequestModel.objects.get_or_create(
        repo=repo, number=pr.number)[0]
    data = defaultdict(dict)

    with lock_igitt_object('label mr', pr):
        labels = pr.labels
        for issue in issues:
            labels = issue.labels | labels
            data[issue.number]['labels'] = list(issue.labels)
        pr.labels = labels

    if sync_assignees:
        with lock_igitt_object('assign mr', pr):
            assignees = pr.assignees
            for issue in issues:
                assignees = set(issue.assignees) | set(assignees)
                data[issue.number]['assignees'] = list(issue.assignees)
            # TODO: reduce the number of requests sent
            for assignee in assignees - set(pr.assignees):
                pr.assign(assignee)

    pr_obj.closes_issues = data
    pr_obj.save()


@ResponderRegistrar.responder(
    'issue_pr_sync',
    IssueActions.REOPENED,
    IssueActions.ATTRIBUTES_CHANGED
)
def sync_pr_with_updated_issue(issue: Issue,
                               sync_assignees: bool='Synchronize Assignees'):
    # Don't move to module code! Apps aren't loaded yet.
    from .models import MergeRequestModel

    issue_num = str(issue.number)
    pr_objects = MergeRequestModel.find_mrs_with_issue(issue)

    for pr_object in pr_objects:
        pr = pr_object.igitt_pr
        pr_data = pr_object.closes_issues[issue_num]
        closes_issues = pr_object.closes_issues
        print(closes_issues)
        other_labels = frozenset().union(*[closes_issues[num]['labels']
                                           for num in closes_issues.keys()
                                           if num != issue_num])

        with lock_igitt_object('label pr', pr):
            labels = pr.labels - set(pr_data['labels'])
            print(labels, other_labels, issue.labels)
            print(issue.labels | labels | other_labels)
            pr.labels = issue.labels | labels | other_labels

        if sync_assignees:
            other_assignees = frozenset().union(
                *[closes_issues[num]['assignees']
                  for num in closes_issues.keys()
                  if num != issue_num])

            with lock_igitt_object('assign mr', pr):
                assignees = set(pr.assignees) - set(pr_data['assignees'])
                assignees = set(issue.assignees) | assignees | other_assignees

                # TODO: reduce the number of requests sent
                for assignee in assignees - set(pr.assignees):
                    pr.assign(assignee)

                for assignee in set(pr_data['assignees']) - assignees:
                    pr.unassign(assignee)

        pr_object.closes_issues.update({
            issue_num: {
                'labels': list(issue.labels),
                'assignees': list(issue.assignees)
            }
        })
        pr_object.save()
