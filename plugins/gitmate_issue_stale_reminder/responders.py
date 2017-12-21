from datetime import datetime
from datetime import timedelta

from celery.schedules import crontab
from IGitt.Interfaces.Actions import IssueActions, MergeRequestActions
from IGitt.Interfaces.Issue import Issue, IssueStates
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Repository import Repository

from gitmate.utils import lock_igitt_object
from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.scheduled_responder(
    'issue_stale_reminder', crontab(minute='0', hour='0,12'), is_active=True)
def add_stale_label_to_issues(
        repo: Repository,
        issue_expire_limit: int = 'Expiry limit in no. of days for issues',
        stale_label: str = 'Label to be used for marking stale',
        unassign: bool = 'Unassign assignees if an issue goes stale',
):
    """
    Assigns the chosen label to issues which haven't been updated in a certain
    period of time.
    """
    minimum_issue_update_time = (datetime.now() -
                                 timedelta(days=issue_expire_limit)).date()
    for issue in repo.search_issues(
            updated_before=minimum_issue_update_time,
            state=IssueStates.OPEN,
    ):
        with lock_igitt_object('label issue', issue):
            if stale_label not in issue.labels:
                issue.labels = issue.labels | {stale_label}
            if unassign and issue.assignees:
                users = ', '.join(f'@{a.username}' for a in issue.assignees)
                issue.assignees = {}
                issue.add_comment(
                    'This issue seems stale!\n\n' +
                    users + ' please reassign yourself if you\'re still '
                    'working on this.\n\n'
                    '(Powered by [GitMate.io](https://gitmate.io))')


@ResponderRegistrar.responder(
    'issue_stale_reminder',
    IssueActions.REOPENED,
    IssueActions.COMMENTED,
    MergeRequestActions.OPENED,
    MergeRequestActions.SYNCHRONIZED
)
def remove_stale_label_from_issues(
        entity: (Issue, MergeRequest),
        *args,
        stale_label: str = 'Label to be used for marking stale issues'
):
    """
    Unassigns the chosen label from issues when they are updated again or if
    they are mentioned from other pull requests.
    """
    if isinstance(entity, MergeRequest):
        issues = entity.mentioned_issues
        for issue in issues:
            with lock_igitt_object('label issue', issue):
                issue.labels = issue.labels - {stale_label}
    else:
        with lock_igitt_object('label issue', entity):
            entity.labels = entity.labels - {stale_label}
