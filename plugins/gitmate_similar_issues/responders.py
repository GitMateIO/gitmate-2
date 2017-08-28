from celery.schedules import crontab
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.Repository import Repository


from gitmate_hooks import ResponderRegistrar


def _update_issues(repo: Repository):
    # TODO: save issues of repository in database.
    pass


@ResponderRegistrar.scheduled_responder(
    'similar_issues', crontab(minute='0', hour='6,18'), is_active=True)
def update_issues(repo: Repository):
    _update_issues(repo)


@ResponderRegistrar.responder('similar_issues', IssueActions.OPENED, IssueActions.REOPENED)
def gitmate_similar_issues(issue: Issue, **kwargs):
    print("HEYA")
    issue.add_comment(f'This repo has {len(issue.repository.issues)} issues')
