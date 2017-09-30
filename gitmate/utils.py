from contextlib import contextmanager
from enum import Enum
from importlib import import_module
import subprocess

from django.apps import AppConfig
from django.conf import settings
from django_pglocks import advisory_lock


@contextmanager
def lock_igitt_object(task: str, igitt_object, refresh_needed=True):
    """
    The IGitt object should have an .url property, so right now this will only
    work with issues and merge requests.
    """
    with advisory_lock(task + igitt_object.url):
        if refresh_needed:
            igitt_object.refresh()
        yield


def run_in_container(image: str, *args: [str], stdin: str=None) -> str:
    """
    Runs a docker container with the specified image and command and returns
    the output.
    """
    process = subprocess.Popen(['docker', 'run', '-i', '--rm', image, *args],
                               stdout=subprocess.PIPE)
    if stdin:
        process.stdin.write(input.encode('utf-8'))
        process.stdin.close()
    process.wait(timeout=settings.CONTAINER_TIMEOUT)
    return process.stdout.read().decode('utf-8')


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


class GitmatePluginConfig(AppConfig):
    """
    Base class for all plugins to import responders and register tasks with
    ``ResponderRegistrar``.
    """
    def ready(self):
        # importing all responders to register tasks
        try:
            import_module(self.name + '.responders')
        except BaseException as exc:
            print(str(exc))
