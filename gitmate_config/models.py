from typing import List
from typing import Optional

from django.apps import apps
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.contrib.postgres import fields as psql_fields
from django.core.exceptions import ValidationError
from django.db import models
from django.http import Http404
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitHub.GitHubInstallation import GitHubInstallation
from IGitt.GitHub.GitHubOrganization import GitHubOrganization
from IGitt.GitLab.GitLabOrganization import GitLabOrganization
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces import Token as IGittToken
from IGitt.Interfaces.Installation import Installation as IGittInstallation
from IGitt.Interfaces.Organization import Organization as IGittOrganization
from IGitt.Interfaces.Repository import Repository as IGittRepository
from rest_framework.reverse import reverse

from gitmate.apps import get_all_plugins
from gitmate_config.enums import GitmateActions
from gitmate_config.enums import Providers


class Installation(models.Model):
    """
    A model to store repository integration information.
    """
    # The users who have adminstrative access over the installation
    admins = models.ManyToManyField(User, related_name='installations')

    # the provider for the installation
    provider = models.CharField(default=None, max_length=32)

    # unique identifier for the installation
    identifier = models.IntegerField(default=None)

    def __str__(self):  # pragma: no cover
        return f'{self.provider}-installation#{self.identifier}'

    @classmethod
    def from_igitt_installation(cls, instance: IGittInstallation):
        """
        Retrieves an Installation model from an IGitt Installation object.
        """
        return cls.objects.get(provider=instance.hoster,
                               identifier=instance.identifier)

    @property
    def igitt_installation(self) -> IGittInstallation:
        """
        Returns the corresponding IGitt Installation object from the stored
        Installation model.
        """
        if self.provider == Providers.GITHUB.value:
            return GitHubInstallation(self.token, self.identifier)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    @property
    def token(self) -> IGittToken:
        """
        Returns the installation token for the specified configuration.
        """
        if self.provider == Providers.GITHUB.value:
            return GitHubInstallationToken(self.identifier,
                                           django_settings.GITHUB_JWT)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    class Meta:
        unique_together = ('provider', 'identifier')


class Organization(models.Model):
    admins = models.ManyToManyField(User, related_name='orgs')
    name = models.CharField(default=None, max_length=255)
    primary_user = models.ForeignKey(User, on_delete=models.CASCADE)
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
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def from_igitt_org(cls, instance: IGittOrganization):
        """
        Retrieves an Organization model from an IGitt Organization instance.

        :param instance: The IGitt Object instance.
        """
        return cls.objects.get(name=instance.name, provider=instance.hoster)

    class Meta:
        unique_together = ('provider', 'name')


class Repository(models.Model):

    # The unique identifier for each repository which never changes
    identifier = models.IntegerField(default=None, null=True)

    # The user who operates the repository
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    # The users who can control the repository
    admins = models.ManyToManyField(User, related_name='admin_repos')

    # The provider for the hosted repository
    provider = models.CharField(default=None, max_length=32)

    # The full name of the repository along with username
    full_name = models.CharField(default=None, max_length=255)

    # The set of active plugins on the repository
    plugins = psql_fields.ArrayField(models.CharField(max_length=255),
                                     default=list)

    active = models.BooleanField(default=False)

    # number of times a repository has been activated
    activation_count = models.IntegerField(default=0)

    # The organization this repository is related to
    org = models.ForeignKey(Organization, null=True, related_name='repos')

    # the installation this repository is related to
    installation = models.ForeignKey(
        Installation, models.SET_NULL, null=True, related_name='repos')

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not any([self.user, self.installation]):
            raise ValidationError(
                'Repository has to be linked to an Installation or a User')
        self.plugins = list(set(self.plugins))
        super(Repository, self).save(*args, **kwargs)

    def get_plugin_settings_with_info(self, request=None):
        """
        Returns the dictionary of settings of all the plugins with their names,
        values, types and descriptions for the specified repository.
        """
        return {
            'repository': reverse('api:repository-detail', args=(self.pk,),
                                  request=request),
            'plugins': [plugin.get_settings_with_info(self)
                        for plugin in get_all_plugins()]
        }

    @property
    def settings(self):
        """
        Returns a dictionary of settings for active plugins in this repo.
        """
        return {k: v for plugin in get_all_plugins(repo=self)
                for k, v in plugin.get_settings(self).items()}

    @settings.setter
    def settings(self, plugins: Optional[List]=None):
        """
        Sets the plugin settings for all plugins for the specified repo.
        """
        # Don't move to module code, causes circular dependency!
        from gitmate_hooks.utils import ResponderRegistrar

        if plugins is None:  # pragma: no cover
            plugins = []

        for plugin in plugins:
            if 'name' not in plugin:
                raise Http404

            # premature 404 because no such plugin is not present
            try:
                config = apps.get_app_config(f"gitmate_{plugin['name']}")
            except LookupError:
                raise Http404

            plugin_name = config.plugin_name

            if 'active' in plugin:
                plugin_exists = plugin_name in self.plugins

                # respond to plugin activation / deactivation
                if plugin['active'] is True and not plugin_exists:
                    self.plugins.append(plugin_name)
                    ResponderRegistrar.respond(
                        GitmateActions.PLUGIN_ACTIVATED,
                        self,
                        repo=self,
                        plugin_name=plugin_name)
                elif plugin['active'] is False and plugin_exists:
                    self.plugins.remove(plugin_name)
                    ResponderRegistrar.respond(
                        GitmateActions.PLUGIN_DEACTIVATED,
                        self,
                        repo=self,
                        plugin_name=plugin_name)
                self.save()

            if 'settings' in plugin and isinstance(plugin['settings'], dict):
                config.set_settings(self, plugin['settings'])

    @classmethod
    def from_igitt_repo(cls, instance: IGittRepository, active: bool=True):
        """
        Retrieves a repository model from an IGitt Repository instance.

        :param instance: The IGitt Repository instance.
        :param active: Filter for active repositories.
        """
        return cls.objects.get(
            identifier=instance.identifier,
            provider=instance.hoster,
            active=active)

    @property
    def token(self) -> IGittToken:
        """
        Returns the IGitt access token for the repository or the installation
        token, if the repository is related to an installation.
        """
        if self.installation is not None:
            return self.installation.token

        raw_token = self.user.social_auth.get(
            provider=self.provider).access_token

        return Providers(self.provider).get_token(
            raw_token,
            private_token='private_token' in self.user.social_auth.get(
                provider=self.provider).extra_data
        )

    @property
    def igitt_repo(self) -> IGittRepository:
        """
        Returns an IGitt Repository object from Repository model.
        """
        if self.provider == Providers.GITHUB.value:
            return GitHubRepository(self.token,
                                    self.identifier or self.full_name)
        if self.provider == Providers.GITLAB.value:
            return GitLabRepository(self.token,
                                    self.identifier or self.full_name)

        # Other providers aren't implemented yet.
        raise NotImplementedError

    class Meta:
        unique_together = ('provider', 'identifier')
        verbose_name_plural = 'repositories'


class SettingsBase(models.Model):
    """
    The abstract base class for all plugin settings.
    """
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='%(app_label)s_settings')

    @property
    def configuration(self):
        """
        Returns the current configuration of the plugin with the name, value,
        description and type of each field.
        """
        return [
            {
                'name': field.name,
                'value': field.value_from_object(self),
                'description': field.help_text,
                'type': field.get_internal_type(),
            }
            for field in self._meta.fields
            if field.name not in ['repo', 'id']
        ]

    class Meta:
        verbose_name_plural = 'settings'
        abstract = True
