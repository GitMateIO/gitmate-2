from importlib import import_module

from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.Interfaces.Repository import Repository

from gitmate_config import Providers


class Plugin(models.Model):
    name = models.CharField(
        # default None ensures that trying to save a Plugin instance
        # with uninitialized name will be forbidden on database level
        default=None, max_length=50, primary_key=True)

    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def import_module(self):
        return import_module('gitmate_' + self.name)

    def get_detailed_plugin_settings(self, repo):
        """
        Returns a detailed dictionary of specified plugin's settings with their
        values, types and descriptions.
        """
        plugin = self.import_module()
        settings = plugin.models.Settings.objects.filter(repo=repo)[0]
        return {
            "status": "active" if self.active else "inactive",
            "settings": {
                field.name: {
                    "value": field.value_from_object(settings),
                    "description": field.help_text,
                    "type": field.get_internal_type(),
                }
                for field in settings._meta.fields
                if field.name not in ['repo', 'id']
            }
        }

    def get_plugin_settings(self, repo):
        """
        Returns the dictionary of settings for the specified plugin.
        """
        plugin = self.import_module()
        settings = plugin.models.Settings.objects.filter(repo=repo)[0]
        return model_to_dict(settings, exclude=['repo', 'id'])

    def set_settings_for_repo(self, repo, settings):
        """
        Sets the plugin settings for this plugin for the specified repo.
        """
        plugin = self.import_module()
        instance = plugin.models.Settings.objects.filter(repo=repo)[0]
        for key, value in settings.items():
            setattr(instance, key, value)
        instance.save()

    @classmethod
    def set_all_settings_for_repo(cls, repo, plugins):
        """
        Sets the plugin settings for all plugins for the specified repo.
        """
        for plugin in plugins:
            if 'name' not in plugin:
                raise Http404
            plugin_obj = get_object_or_404(Plugin, name=plugin['name'])
            if 'status' in plugin and isinstance(plugin['status'], str):
                if plugin['status'] == 'active':
                    plugin_obj.active = True
                elif plugin['status'] == 'inactive':
                    plugin_obj.active = False
            if 'settings' in plugin:
                if isinstance(plugin['settings'], dict):
                    plugin_obj.set_settings_for_repo(repo, plugin['settings'])
            plugin_obj.save()

    @classmethod
    def get_all_settings_by_repo(cls, repo):
        """
        Returns the dictionary of settings of all the plugins with their names,
        values, types and descriptions for the specified repository.
        """
        return {
            'repository': repo.full_name,
            'plugins': {plugin.name: plugin.get_detailed_plugin_settings(repo)
                        for plugin in cls.objects.all()}
        }

    @classmethod
    def get_all_settings_by_user(cls, user):
        """
        Returns the dictionary of settings of all the plugins with their names,
        values, types and descriptions for all the repositories of the
        specified user.
        """
        return [Plugin.get_all_settings_by_repo(repo)
                for repo in Repository.objects.filter(user=user)]

    @classmethod
    def get_all_settings(cls, repo, format=None):
        """
        Returns a dictionary of values for settings of all the plugins.
        """
        return {k: v for plugin in cls.objects.all()
                for k, v in plugin.get_plugin_settings(repo).items()}


class Repository(models.Model):

    # The user who owns the repository
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The provider for the hosted repository
    provider = models.CharField(default=None, max_length=32)

    # The full name of the repository along with username
    full_name = models.CharField(default=None, max_length=255)

    active = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    def igitt_repo(self) -> Repository:
        token = self.user.social_auth.get(
            provider=self.provider).extra_data['access_token']
        if self.provider == Providers.GITHUB.value:
            return GitHubRepository(token, self.full_name)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    class Meta:
        unique_together = ('provider', 'full_name')
