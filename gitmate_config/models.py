from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Repository import Repository
from rest_framework.reverse import reverse

from gitmate_config import Providers

class Plugin(models.Model):
    name = models.CharField(
        # default None ensures that trying to save a Plugin instance
        # with uninitialized name will be forbidden on database level
        default=None, max_length=50, primary_key=True)

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        return 'gitmate_' + self.name

    @property
    def importable(self):
        try:
            self.import_module().models
            return True
        except:
            return False

    def import_module(self):
        return import_module(self.full_name)

    def config_value(self, key, default=None):
        return getattr(apps.get_app_config(self.full_name), key, default)

    def get_settings_with_info(self, repo):
        """
        Returns a detailed dictionary of specified plugin's settings with their
        values, types and descriptions.
        """
        plugin = self.import_module()
        settings, _ = plugin.models.Settings.objects.get_or_create(repo=repo)
        return {
            'name': self.name,
            'title': self.config_value('verbose_name', None),
            'description': self.config_value('description', ''),
            'active': repo.plugins.filter(name=self).exists(),
            'settings': [
                {
                    'name': field.name,
                    'value': field.value_from_object(settings),
                    'description': field.help_text,
                    'type': field.get_internal_type(),
                }
                for field in settings._meta.fields
                if field.name not in ['repo', 'id']
            ]
        }

    def get_settings(self, repo):
        """
        Returns the dictionary of settings for the specified plugin.
        """
        plugin = self.import_module()
        settings, _ = plugin.models.Settings.objects.get_or_create(repo=repo)
        return model_to_dict(settings, exclude=['repo', 'id'])

    def set_settings(self, repo, settings):
        """
        Sets the plugin settings for this plugin for the specified repo.
        """
        plugin = self.import_module()
        instance, _ = plugin.models.Settings.objects.get_or_create(repo=repo)
        for name, value in settings.items():
            setattr(instance, name, value)
        instance.save()


class Repository(models.Model):
    # The user who operates the repository
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The users who can control the repository
    admins = models.ManyToManyField(User, related_name='admin_repos')

    # The provider for the hosted repository
    provider = models.CharField(default=None, max_length=32)

    # The full name of the repository along with username
    full_name = models.CharField(default=None, max_length=255)

    # The set of active plugins on the repository
    plugins = models.ManyToManyField(Plugin)

    active = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    def get_plugin_settings(self):
        """
        Returns a dictionary of settings for active plugins in this repo.
        """
        return {k: v for plugin in self.plugins.all()
                for k, v in plugin.get_settings(self).items()
                if plugin.importable}

    def get_plugin_settings_with_info(self, request=None):
        """
        Returns the dictionary of settings of all the plugins with their names,
        values, types and descriptions for the specified repository.
        """
        return {
            'repository': reverse('api:repository-detail', args=(self.pk,),
                                  request=request),
            'plugins': [plugin.get_settings_with_info(self)
                        for plugin in Plugin.objects.all()
                        if plugin.importable]
        }

    def set_plugin_settings(self, plugins=[]):
        """
        Sets the plugin settings for all plugins for the specified repo.
        """
        for plugin in plugins:
            if 'name' not in plugin:
                raise Http404
            plugin_obj = get_object_or_404(Plugin, name=plugin['name'])

            if not plugin_obj.importable:
                raise Http404

            if 'active' in plugin:
                if plugin['active'] is True:
                    self.plugins.add(plugin_obj)
                else:
                    self.plugins.remove(plugin_obj)
                self.save()

            if 'settings' in plugin:
                if isinstance(plugin['settings'], dict):
                    plugin_obj.set_settings(self, plugin['settings'])

    def igitt_repo(self) -> Repository:
        token = self.user.social_auth.get(
            provider=self.provider).extra_data['access_token']
        if self.provider == Providers.GITHUB.value:
            return GitHubRepository(token, self.full_name)
        if self.provider == Providers.GITLAB.value:
            return GitLabRepository(token, self.full_name)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    class Meta:
        unique_together = ('provider', 'full_name')
