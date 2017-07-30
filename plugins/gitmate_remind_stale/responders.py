from datetime import datetime
from datetime import timedelta
from celery.schedules import crontab
from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Repository import Repository as IGittRepository
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate.utils import ScheduledTasks
from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.scheduler(crontab(minute='0', hour='0'))
def start_reminding():
    # Don't move to module code! Apps aren't loaded yet.
    from gitmate_config.models import Plugin

    plugin = Plugin.objects.get(name='remind_stale')
    for repo in plugin.repository_set.filter(active=True):
        ResponderRegistrar.respond(
            ScheduledTasks.DAILY,
            repo,
            repo.igitt_repo,
            options=repo.get_plugin_settings())


@ResponderRegistrar.responder('remind_stale', ScheduledTasks.DAILY)
def add_stale_label(
        repo: IGittRepository,
        days: int = 7,
        stale_label: str = 'status/STALE'
):
    minimum_update_time = (datetime.now() - timedelta(days=days)).date()

    for issue in repo.search_issues(updated_before=minimum_update_time):
        with lock_igitt_object('label issue', issue):
            if stale_label not in issue.labels:
                issue.labels = issue.labels | {stale_label}

    for mr in repo.search_mrs(updated_before=minimum_update_time):
        with lock_igitt_object('label mr', mr):
            if stale_label not in mr.labels:
                mr.labels = mr.labels | {stale_label}


@ResponderRegistrar.responder(
    'remind_stale',
    IssueActions.CLOSED,
    IssueActions.REOPENED,
    IssueActions.COMMENTED,
    IssueActions.ATTRIBUTES_CHANGED,
    MergeRequestActions.CLOSED,
    MergeRequestActions.REOPENED,
    MergeRequestActions.SYNCHRONIZED,
    MergeRequestActions.COMMENTED,
    MergeRequestActions.ATTRIBUTES_CHANGED
)
def remove_stale_label(pr: MergeRequest, stale_label: str='status/STALE'):
    with lock_igitt_object('label mr', pr):
        pr.labels = pr.labels - {stale_label}
