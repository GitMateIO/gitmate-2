from contextlib import contextmanager
from glob import glob
from importlib import import_module
from os import listdir
from os import path
import subprocess

from django.apps import apps
from django.apps import AppConfig
from django.forms.models import model_to_dict
from django_pglocks import advisory_lock

from gitmate.exceptions import MissingSettingsError


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
    existing_files = glob(directory + '/**/*.py', recursive=True)
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


def run_in_container(image: str, *args: [str], stdin: str=None) -> str:
    """
    Runs a docker container with the specified image and command and returns
    the output.
    """
    process = subprocess.Popen(['docker', 'run', '-i', '--rm', image, *args],
                               stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE if stdin else None)
    if stdin:
        process.stdin.write(stdin.encode('utf-8'))
        process.stdin.close()
    retval = process.stdout.read().decode('utf-8')
    process.wait()
    return retval


def snake_case_to_camel_case(string: str):
    """
    Converts a string from snake_case to CamelCase.
    """
    return ''.join(group.capitalize() or '_' for group in string.split('_'))


class GitmatePluginConfig(AppConfig):
    """
    Base class for all plugins to import responders and register tasks with
    ``ResponderRegistrar``.
    """
    enable_on_repo_activation = False
    plugin_category = None
    description = None

    @property
    def full_name(self):
        """
        Returns the full module path of the plugin with `plugins` as module
        root. Useful for django application identification.
        """
        return self.name[8:]

    @property
    def plugin_name(self):
        """
        Returns the name of the plugin.
        """
        return self.name[16:]

    @property
    def settings_model(self):
        """
        Returns the settings model associated with the plugin.
        """
        return apps.get_model(self.full_name, 'Settings')

    @property
    def importable(self):
        try:
            self.settings_model
            return True
        except MissingSettingsError:  # pragma: no cover
            return False

    def ready(self):
        # ensure that all plugin names start with `plugins.gitmate_`
        assert self.name.startswith('plugins.gitmate_')

        # importing all responders to register tasks
        try:
            import_module(self.name + '.responders')
        except BaseException as exc:
            print(str(exc))

    def _default_settings(self, repo):
        return self.settings_model.objects.get_or_create(repo=repo)[0]

    def get_settings_with_info(self, repo):
        """
        Returns a detailed dictionary of specified plugin's settings with their
        values, types and descriptions.
        """
        settings = self._default_settings(repo)
        return {
            'name': self.plugin_name,
            'title': self.verbose_name,
            'plugin_category': self.plugin_category.value,
            'description': self.description,
            'active': self.plugin_name in repo.plugins,
            'settings': settings.configuration
        }

    def get_settings(self, repo):
        """
        Returns the dictionary of settings for the specified plugin.
        """
        settings = self._default_settings(repo)
        return model_to_dict(settings, exclude=['repo', 'id'])

    def set_settings(self, repo, settings):
        """
        Sets the plugin settings for this plugin for the specified repo.
        """
        instance = self._default_settings(repo)
        for name, value in settings.items():
            setattr(instance, name, value)
        instance.save()
