from collections import OrderedDict
from hashlib import sha1
import hmac
import inspect
import os
import re

from django.apps import apps
from django.apps.registry import Apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core import management
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth
from vcr import VCR
import pytest

from gitmate.utils import snake_case_to_camel_case
from gitmate_config.enums import Providers
from gitmate_config.models import Installation
from gitmate_config.models import Organization
from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_hooks.utils import ResponderRegistrar
from gitmate_hooks.views import github_webhook_receiver
from gitmate_hooks.views import gitlab_webhook_receiver


FILTER_QUERY_PARAMS = ['access_token', 'private_token']
FILTER_PARAMS_REGEX = re.compile(r'(\??)((?:{})=\w+&?)'.format(
    '|'.join(FILTER_QUERY_PARAMS)))

# this is a helper method to reinitate gitmate plugins and is used only
# for testing purposes and is not a part of the actual gitmate server,
# henceforth coverage here is not required.


def reinit_plugin(name, upmate: bool=False):  # pragma: no cover
    """
    Reinitialize gitmate with plugin and upmate, if specified.
    """
    app_name = 'gitmate_' + name
    app_config_name = 'plugins.{}.apps.{}Config'.format(
        app_name, snake_case_to_camel_case(app_name))

    if app_config_name in settings.INSTALLED_APPS:
        return

    settings.GITMATE_PLUGINS += [name]
    settings.INSTALLED_APPS += [app_config_name]
    # To load the new app let's reset app_configs, the dictionary
    # with the configuration of loaded apps
    apps.app_configs = OrderedDict()
    # set ready to false so that populate will work
    apps.ready = False
    # re-initialize them all
    apps.populate(settings.INSTALLED_APPS)

    # migrate the models
    management.call_command('migrate', app_name, interactive=False)

    # upmate the plugins, if specified
    if upmate is True:
        management.call_command('upmate', interactive=False)


class StreamMock:
    """
    A class for mocking standard input, output and error streams.
    """

    def __init__(self, value):
        self.value = value

    def read(self):
        return self.value.encode()

    def write(self, value):
        assert self.value == value.decode()

    def close(self):
        pass


@pytest.mark.usefixtures('vcrpy_record_mode')
class RecordedTestCase(TransactionTestCase):
    enable_unused_record_deletion = True

    @staticmethod
    def remove_link_headers(resp):
        for i, link in enumerate(resp['headers'].get('Link', [])):
            resp['headers']['Link'][i] = FILTER_PARAMS_REGEX.sub(r'\1', link)
        return resp

    def _get_cassette_name(self):
        return '{0}.{1}.yaml'.format(self.__class__.__name__,
                                     self._testMethodName)

    def _get_vcr(self):
        testdir = os.path.dirname(inspect.getfile(self.__class__))
        cassettes_dir = os.path.join(testdir, 'cassettes')
        return VCR(
            record_mode=self.vcrpy_record_mode,
            cassette_library_dir=cassettes_dir,
            match_on=['method', 'scheme', 'host', 'port', 'path'],
            filter_query_parameters=FILTER_QUERY_PARAMS,
            filter_post_data_parameters=FILTER_QUERY_PARAMS,
            before_record_response=RecordedTestCase.remove_link_headers)

    def tearDown(self):  # pragma: no cover
        # Check the cassette for unused interactions and remove them
        if (not self.cassette.all_played and self.enable_unused_record_deletion
                and not self.cassette.dirty):
            self.cassette.data = [
                v for i, v in enumerate(self.cassette.data)
                if self.cassette.play_counts[i] >= 1
            ]
            self.cassette._save(force=True)

    @classmethod
    def setUpClass(cls):
        """
        On inherited classes, run `setUp` method as usual.

        Inspired via http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/17696807#17696807
        """
        if (cls is not RecordedTestCase and
                cls.setUp is not RecordedTestCase.setUp):
            _setUp = cls.setUp

            def newSetUp(self, *args, **kwargs):
                RecordedTestCase.setUp(self)
                return _setUp(self, *args, **kwargs)

            cls.setUp = newSetUp

    def setUp(self):
        # use vcrpy recorder
        myvcr = self._get_vcr()
        context_manager = myvcr.use_cassette(self._get_cassette_name())
        self.cassette = context_manager.__enter__()
        self.addCleanup(context_manager.__exit__, None, None, None)


class MigrationTestCase(RecordedTestCase):
    migrate_from = None
    migrate_to = None
    app = None

    def tearDown(self):
        # run the migration all the way forward after testing
        management.call_command(
            'migrate', self.app, verbosity=0, interactive=False)

    def setUp(self):
        self.assertTrue(
            self.app and self.migrate_from and self.migrate_to,
            f"A MigrationTestCase subclass, '{type(self).__name__}' must "
            'define app, migrate_from and migrate_to properties.')

        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        # Run any configuration setup before testing the migration
        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps: Apps):  # pragma: no cover
        pass


class GitmateTestCase(RecordedTestCase):
    """
    A base class for setting up a dummy user, request factory and a repo for
    the user.
    """
    active = False
    upmate = True

    def setUp(self):
        # Reconfigure gitmate for tests
        reinit_plugin('testplugin', upmate=self.upmate)

        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            username='john',
            email='john.appleseed@example.com',
            first_name='John',
            last_name='Appleseed'
        )

        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value, uid=1)
        self.auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN'],
            'id': 16681030,
        })
        self.auth.save()
        self.gl_auth = UserSocialAuth(
            user=self.user, provider=Providers.GITLAB.value, uid=2
        )
        self.gl_auth.set_extra_data({
            'access_token': os.environ['GITLAB_TEST_TOKEN'],
            'id': 1369631,
        })
        self.gl_auth.save()
        self.gh_app_auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB_APP.value, uid=1)
        self.gh_app_auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN'],
            'id': 16681030
        })
        self.gh_app_auth.save()

        self.repo = Repository(
            user=self.user,
            identifier=49558751,
            full_name=os.environ['GITHUB_TEST_REPO'],
            provider=Providers.GITHUB.value,
            active=self.active)
        self.repo.save()  # Needs an ID before adding relationship

        self.org = Organization(
            name=os.environ['GITHUB_TEST_REPO'].split('/', maxsplit=1)[0],
            primary_user=self.user,
            provider='github',
        )
        self.org.save()  # Needs an ID before adding relationship

        self.gh_inst = Installation(provider='github', identifier=1)
        self.gh_inst.save()  # Needs an ID before adding relationship
        self.gh_inst.admins.add(self.user)
        self.gh_inst.save()

        self.gh_app_repo = Repository(
            identifier=49558751,
            full_name=os.environ['GITHUB_TEST_REPO'],
            provider=Providers.GITHUB_APP.value,
            active=self.active,
            installation=self.gh_inst
        )
        self.gh_app_repo.save()  # Needs an ID before adding relationship

        self.repo.admins.add(self.user)
        self.org.admins.add(self.user)
        self.repo.save()
        self.org.save()
        self.gl_repo = Repository(
            user=self.user,
            identifier=3439658,
            full_name=os.environ['GITLAB_TEST_REPO'],
            provider=Providers.GITLAB.value,
            active=self.active)
        self.gl_repo.save()
        self.gl_repo.admins.add(self.user)
        self.gl_repo.save()

    def setUpWithPlugin(self, name: str):
        self.plugin = Plugin(name=name)
        self.plugin_module = self.plugin.import_module()
        self.plugin.save()

        GitmateTestCase.setUp(self)

        self.repo.plugins.add(self.plugin)
        self.repo.active = True
        self.repo.save()

        self.gl_repo.plugins.add(self.plugin)
        self.gl_repo.active = True
        self.gl_repo.save()

    def simulate_scheduled_responder_call(self, event: str, repo: Repository):
        ResponderRegistrar.respond(event, repo.igitt_repo, repo=repo)

    def simulate_github_webhook_call(self, event: str, data: dict):
        request = self.factory.post(
            reverse('webhooks:github'), data, format='json')
        hashed = hmac.new(
            bytes(os.environ['WEBHOOK_SECRET'], 'utf-8'),
            request.body,
            sha1)
        signature = 'sha1=' + hashed.hexdigest()
        request.META.update({
            'HTTP_X_HUB_SIGNATURE': signature,
            'HTTP_X_GITHUB_EVENT': event,
        })

        return github_webhook_receiver(request)

    def simulate_gitlab_webhook_call(self, event: str, data: dict):
        request = self.factory.post(
            reverse('webhooks:gitlab'), data, format='json')
        request.META.update({
            'HTTP_X_GITLAB_TOKEN': os.environ['WEBHOOK_SECRET'],
            'HTTP_X_GITLAB_EVENT': event
        })
        return gitlab_webhook_receiver(request)
