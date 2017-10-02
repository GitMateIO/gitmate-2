from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Issue import Issue

from gitmate.utils import lock_igitt_object
from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.responder('issue_assigner', IssueActions.OPENED)
def add_assignees_to_issue(
    issue: Issue,
    keywords: dict() = 'Keywords that trigger assignments',
):
    issue_summary = issue.title.lower() + ' ' + issue.description.lower()
    new_assignees = {
        assignee
        for assignee, l_keywords in keywords.items()
        for keyword in l_keywords.split(',')
        if keyword.strip() and keyword in issue_summary
    }

    with lock_igitt_object('assign issue', issue, refresh_needed=False):
        for assignee in new_assignees:
            issue.assign(assignee)
