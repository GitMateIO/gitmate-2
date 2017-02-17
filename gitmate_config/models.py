from importlib import import_module

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models
from django.forms.models import model_to_dict


class Plugin(models.Model):
    name = models.CharField(
        # default None ensures that trying to save a Plugin instance
        # with uninitialized name will be forbidden on database level
        default=None, max_length=50)

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

    @classmethod
    def get_all_settings_detailed(cls, repo):
        """
        Returns the dictionary of settings of all the plugins with their names,
        values, types and descriptions.
        """
        return {plugin.name: plugin.get_detailed_plugin_settings(repo)
                for plugin in cls.objects.all()}

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

    class Meta:
        unique_together = ('provider', 'full_name')
