from contextlib import contextmanager
from enum import Enum
from glob import glob
from importlib import import_module
from os import listdir
from os import path
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


def is_plugin(directory: str) -> bool:
    """
    Checks whether the given directory is a GitMate plugin.

    :param directory: The absolute path of the directory to be checked.
    :return:          True if the directory contains all the files required for
                      it to be a plugin, otherwise False.
    """
    files_to_be_present = {'__init__.py',
                           'apps.py',
                           'models.py',
                           'responders.py',
                           'migrations/__init__.py'}
    existing_files = glob(directory + "/**/*.py", recursive=True)
    return all(path.join(directory, f) in existing_files
               for f in files_to_be_present)


def get_plugins() -> [str]:
    """
    Retrieves the list of plugins from the `plugins` directory.
    """
    root = path.dirname(path.dirname(path.abspath(__file__)))
    plugin_dir = path.join(root, 'plugins')
    return [dir.replace('gitmate_', '')
            for dir in listdir(plugin_dir)
            if path.isdir(path.join(plugin_dir, dir))
            and dir.startswith('gitmate_')
            and is_plugin(path.abspath(path.join(plugin_dir, dir)))]


def run_in_container(image: str, *args: [str], stdin: str='') -> str:
    """
    Runs a docker container with the specified image and command and returns
    the output.
    """
    process = subprocess.Popen(['docker', 'run', '-i', '--rm', image, *args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE if stdin else None)
    stdout, _ = process.communicate(stdin.encode('utf-8'),
                                    settings.CONTAINER_TIMEOUT)
    return stdout.decode('utf-8')


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
