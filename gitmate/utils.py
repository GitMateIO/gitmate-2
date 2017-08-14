from contextlib import contextmanager
from enum import Enum


from django_pglocks import advisory_lock


@contextmanager
def lock_igitt_object(task: str, igitt_object):
    """
    The IGitt object should have an .url property, so right now this will only
    work with issues and merge requests.
    """
    with advisory_lock(task + igitt_object._url):
        igitt_object.refresh()
        yield

class PluginCategory(Enum):
    """
    Enum class to hold types of plugins.
    """
    # Plugin related to analysis
    ANALYSIS = 'analysis'
    # Plugin related to issues
    ISSUE = 'issue'
    # Plugin related to Pull Requests
    PULLS = 'pull_request'


def snake_case_to_camel_case(string: str):
    """
    Converts a string from snake_case to CamelCase.
    """
    return ''.join(group.capitalize() or '_' for group in string.split('_'))

class ScheduledTasks(Enum):
    """
    Task schedules type
    """
    # Scheduled to run daily
    DAILY = 1
    # Scheduled to run weekly
    WEEKLY = 2
    # Scheduled to run monthy
    MONTHLY = 3
