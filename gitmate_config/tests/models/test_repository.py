from django.core.validators import ValidationError
from django.db import IntegrityError
from django.http import Http404
import pytest
from rest_framework.reverse import reverse

from IGitt.GitHub import GitHubToken
from IGitt.GitHub import GitHubInstallationToken
from IGitt.GitLab import GitLabOAuthToken

from gitmate_config.models import Repository
from gitmate_config.tests.test_base import GitmateTestCase


class TestRepository(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')
        self.full_name = 'test'
        self.provider = 'example'

    def test__str__(self):
        repo = Repository(full_name=self.full_name,
                          provider=self.provider, user=self.user)
        assert str(repo) == self.full_name

    def test_defaults(self):
        repo = Repository(user=self.user)
        # checking default values
        assert not repo.active
        assert repo.full_name is None
        assert repo.provider is None
        # Don't allow none objects to be saved
        with pytest.raises(IntegrityError):
            repo.save()

    def test_validation(self):
        repo = Repository(user=self.user)
        # don't allow empty strings
        repo.full_name = ''
        repo.provider = ''
        with pytest.raises(ValidationError):
            repo.full_clean()

    def test_user(self):
        repo = Repository(
            full_name=self.full_name, provider=self.provider, identifier=0)
        # Don't allow saving if not linked to a user
        with pytest.raises(ValidationError):
            repo.save()

    def test_token(self):
        self.assertIsInstance(self.repo.token, GitHubToken)
        self.assertIsInstance(self.gh_app_repo.token, GitHubInstallationToken)
        self.assertIsInstance(self.gl_repo.token, GitLabOAuthToken)

    def test_set_plugin_settings(self):
        # add a plugin into it
        self.repo.plugins.append(self.plugin)
        self.repo.save()

        old_settings = self.repo.settings

        # No proper plugin name
        new_settings = [{
            'active': True,
            'settings': {}
        }]
        with pytest.raises(Http404):
            self.repo.settings = new_settings
        modified_settings = self.repo.settings
        assert modified_settings == old_settings

        # No status setting
        new_settings = [{
            'name': 'testplugin',
            'settings': {}
        }]
        self.repo.settings = new_settings
        modified_settings = self.repo.settings
        assert modified_settings == old_settings

        # Undefined plugin
        new_settings = [{
            'name': 'undefinedplugin'
        }]
        with pytest.raises(Http404):
            self.repo.settings = new_settings
        modified_settings = self.repo.settings
        assert modified_settings == old_settings

        # Remove all plugins
        new_settings = [{
            'name': 'testplugin',
            'active': False,
        }]
        self.repo.settings = new_settings
        modified_settings = self.repo.settings
        assert modified_settings == {}

        # Successful set
        new_settings = [{
            'name': 'testplugin',
            'active': True,
            'settings': {
                'example_bool_setting': False,
                'example_char_setting': 'hello'
            }
        }]
        self.repo.settings = new_settings

        modified_settings = self.repo.settings
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == 'hello'

    def test_plugin_set_settings_not_importable(self):
        new_settings = [{
            'name': 'fake_plugin',
            'settings': {
                'jedi': True
            }
        }]
        with pytest.raises(Http404):
            self.repo.settings = new_settings

    def test_get_plugin_settings_with_info(self):
        # add a plugin into it
        self.repo.plugins.append(self.plugin)
        self.repo.save()

        settings = self.repo.get_plugin_settings_with_info()
        self.assertIn(
            {
                'name': 'testplugin',
                'title': 'Testing',
                'plugin_category': 'issue',
                'description': (
                        'A simple plugin used for testing. Smile :)'
                ),
                'active': True,
                'settings': [
                    {
                        'name': 'example_char_setting',
                        'value': 'example',
                        'description': 'An example Char setting',
                        'type': 'CharField'
                    },
                    {
                        'name': 'example_bool_setting',
                        'value': True,
                        'description': 'An example Bool setting',
                        'type': 'BooleanField'
                    },
                ]
            },
            settings['plugins'])
        self.assertEqual(settings['repository'],
                         reverse('api:repository-detail',
                                 args=(self.repo.pk,)))
