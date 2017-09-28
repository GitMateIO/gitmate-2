from datetime import datetime, timedelta

import attr
import logging
from importlib import import_module

import stripe

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
from stripe.error import InvalidRequestError

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


@attr.s
class Plan:
    id = attr.ib()
    name = attr.ib()
    max_users = attr.ib()
    trial_days = attr.ib(default=30)

    def fits(self, billable_users):
        return self.max_users is None or billable_users < self.max_users


PLAN_OBJECTS = [
    Plan(1, 'Basic', 8, None),  # Free plan, no trial
    Plan(2, 'Professional', 200),
    Plan(3, 'Business', None),
]

PLANS = {plan.name: plan for plan in PLAN_OBJECTS}


class Organization(models.Model):
    """
    Represents a GitHub or GitLab organization.

    This will automatically create and manage the corresponding stripe
    customer for you and keep the billable users up to date (cached for a day
    at least and updated when you instanciate the class).
    """
    admins = models.ManyToManyField(User, related_name='orgs')
    name = models.CharField(default=None, max_length=255)
    primary_user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(default=None, max_length=32)

    # Do not set this, generated automatically
    stripe_customer_id = models.CharField(default=None, null=True,
                                          max_length=255)
    billable_users = models.IntegerField(default=None, null=True)
    billable_users_updated = models.DateTimeField(default=None, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.stripe_customer_id is None:
            self._create_customer()
        else:
            logging.info(f'NO UPDATE NEEDED')

        if self._bill_usrs_needs_update:
            logging.info(f'Updating billable users for {self}')
            self.billable_users = self.igitt_org.billable_users
            self.billable_users_updated = datetime.now()
            self.save()
        else:
            logging.info(f'NO UPDATE NEEDED')

        self._update_subscription()

    def _create_customer(self):
        logging.info(f'Creating initial stripe customer for {self}.')
        self._stripe_customer = stripe.Customer.create(
            email=self.primary_user.email,
            description=f'{self.provider}:{self.name}'
        )
        self.stripe_customer_id = self._stripe_customer.stripe_id
        self.save()

    @property
    def _bill_usrs_needs_update(self):
        return self.billable_users is None or \
               self.billable_users_updated < datetime.now() - timedelta(days=1)

    def needed_plan(self):
        logging.info('Determining needed plan')
        for plan in PLAN_OBJECTS:
            if plan.fits(self.billable_users):
                logging.info(f'Needed plan is {plan.name}')
                return plan

        raise AssertionError('No fitting plan available')

    def _create_subscription(self, plan):
        logging.info(f'Creating subscription for {self.name} for '
                     f'{plan.name}')
        stripe.Subscription.create(
            customer=self.stripe_customer_id,
            trial_period_days=plan.trial_days,
            tax_percent=19,
            quantity=self.billable_users,
            plan=plan.id,
        )

    def _update_subscription(self):
        logging.info(f'Updating subscriptions for {self.name}')
        subscriptions = list(self.stripe_customer.subscriptions.all())
        if len(subscriptions) == 0:
            logging.info('Creating initial subscription')
            return self._create_subscription(self.needed_plan())

        assert len(subscriptions) == 1, f'Too many subscriptions for ' \
                                        f'{self.name}'

        subscription = subscriptions[0]
        plan = PLANS[subscription.plan.name]
        if not plan.fits(self.billable_users):
            subscription.quantity = self.billable_users
            subscription.plan = self.needed_plan()
            subscription.trial_end = int(
                (datetime.now() + timedelta(days=30)).timestamp()
            )
            logging.warning(
                f'The organization {self.name} has been upgraded automatically '
                f'and no email has been sent. You should slowly think about '
                f'implementing that feature man!'
            )
            return self._create_subscription(self.needed_plan())

        if self.billable_users != subscription.quantity:
            subscription.quantity = self.billable_users
            subscription.save()

    @property
    def stripe_customer(self):
        """
        Gets you a stripe Customer object to work with and caches it lazily :)
        """
        if self._stripe_customer is None:
            try:
                self._stripe_customer = stripe.Customer.retrieve(
                    self.stripe_customer_id)
            except InvalidRequestError:
                self._create_customer()

        return self._stripe_customer

    @property
    def is_active(self):
        return self.billable_users <= 8

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

    # The organization this repository is related to
    org = models.ForeignKey(Organization, null=True, related_name='repos')

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
