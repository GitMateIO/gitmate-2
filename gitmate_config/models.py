from importlib import import_module

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from IGitt.GitHub.GitHubOrganization import GitHubOrganization
from IGitt.GitLab.GitLabOrganization import GitLabOrganization
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Organization import Organization as IGittOrganization
from IGitt.Interfaces.Repository import Repository as IGittRepository
from rest_framework.reverse import reverse

from gitmate_config import GitmateActions
from gitmate_config import Providers
from gitmate_hooks import ResponderRegistrar


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
        return import_module(self.config_value('name'))

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
            'plugin_category': self.config_value('plugin_category',
                                                 None).value,
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


class Organization(models.Model):
    admins = models.ManyToManyField(User, related_name='orgs')
    name = models.CharField(default=None, max_length=255)
    primary_user = models.OneToOneField(User, on_delete=models.CASCADE)
    provider = models.CharField(default=None, max_length=32)

    def __str__(self):
        return '{}:{}'.format(self.provider, self.name)

    @property
    def igitt_org(self) -> IGittOrganization:
        """
        Returns an IGitt Organization object from Organization model.
        """
        token_str = self.primary_user.social_auth.get(
            provider=self.provider).extra_data['access_token']
        if self.provider == Providers.GITHUB.value:
            token = Providers.GITHUB.get_token(token_str)
            return GitHubOrganization(token, self.name)
        if self.provider == Providers.GITLAB.value:
            token = Providers.GITLAB.get_token(token_str)
            return GitLabOrganization(token, self.name)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    @classmethod
    def from_igitt_org(cls, instance: IGittOrganization):
        """
        Retrieves an Organization model from an IGitt Organization instance.

        :param instance: The IGitt Object instance.
        """
        return cls.objects.get(name=instance.name, provider=instance.hoster)


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
                plugin_exists = self.plugins.filter(pk=plugin_obj.pk).exists()

                # respond to plugin activation / deactivation
                if plugin['active'] is True and plugin_exists is False:
                    self.plugins.add(plugin_obj)
                    ResponderRegistrar.respond(
                        GitmateActions.PLUGIN_ACTIVATED, self, self,
                        plugin_name=plugin['name'])
                elif plugin['active'] is False and plugin_exists is True:
                    self.plugins.remove(plugin_obj)
                    ResponderRegistrar.respond(
                        GitmateActions.PLUGIN_DEACTIVATED, self, self,
                        plugin_name=plugin['name'])
                self.save()

            if 'settings' in plugin:
                if isinstance(plugin['settings'], dict):
                    plugin_obj.set_settings(self, plugin['settings'])

    @classmethod
    def from_igitt_repo(cls, instance: IGittRepository, active: bool=True):
        """
        Retrieves a repository model from an IGitt Repository instance.

        :param instance: The IGitt Repository instance.
        :param active: Filter for active repositories.
        """
        return cls.objects.get(
            full_name=instance.full_name,
            provider=instance.hoster,
            active=active)

    @property
    def igitt_repo(self) -> IGittRepository:
        """
        Returns an IGitt Repository object from Repository model.
        """
        token_str = self.user.social_auth.get(
            provider=self.provider).extra_data['access_token']
        if self.provider == Providers.GITHUB.value:
            token = Providers.GITHUB.get_token(token_str)
            return GitHubRepository(token, self.full_name)
        if self.provider == Providers.GITLAB.value:
            token = Providers.GITLAB.get_token(token_str)
            return GitLabRepository(token, self.full_name)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    class Meta:
        unique_together = ('provider', 'full_name')
        verbose_name_plural = 'repositories'


class SettingsBase(models.Model):
    """
    The abstract base class for all plugin settings.
    """
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='%(app_label)s_repository')

    class Meta:
        verbose_name_plural = 'settings'
        abstract = True
