from django.core.validators import ValidationError
from django.db import IntegrityError
from django.http import Http404
import pytest
from rest_framework.reverse import reverse

from gitmate_config.models import Plugin
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
        repo = Repository(full_name=self.full_name, provider=self.provider)
        # Don't allow saving if not linked to a user
        with pytest.raises(ValidationError):
            repo.full_clean()
        with pytest.raises(IntegrityError):
            repo.save()

    def test_set_plugin_settings(self):
        # add a plugin into it
        self.repo.plugins.add(self.plugin)
        self.repo.save()

        old_settings = self.repo.get_plugin_settings()

        # No proper plugin name
        new_settings = [{
            'active': True,
            'settings': {}
        }]
        with pytest.raises(Http404):
            self.repo.set_plugin_settings(new_settings)
        modified_settings = self.repo.get_plugin_settings()
        assert modified_settings == old_settings

        # No status setting
        new_settings = [{
            'name': 'testplugin',
            'settings': {}
        }]
        self.repo.set_plugin_settings(new_settings)
        modified_settings = self.repo.get_plugin_settings()
        assert modified_settings == old_settings

        # Undefined plugin
        new_settings = [{
            'name': 'undefinedplugin'
        }]
        with pytest.raises(Http404):
            self.repo.set_plugin_settings(new_settings)
        modified_settings = self.repo.get_plugin_settings()
        assert modified_settings == old_settings

        # Remove all plugins
        new_settings = [{
            'name': 'testplugin',
            'active': False,
        }]
        self.repo.set_plugin_settings(new_settings)
        modified_settings = self.repo.get_plugin_settings()
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
        self.repo.set_plugin_settings(new_settings)

        modified_settings = self.repo.get_plugin_settings()
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == 'hello'

    def test_plugin_set_settings_not_importable(self):
        # create a fake plugin
        plugin = Plugin('fake_plugin')
        plugin.save()
        # try to import it
        assert plugin.importable == False

        new_settings = [{
            'name': 'fake_plugin',
            'settings': {
                'jedi': True
            }
        }]
        with pytest.raises(Http404):
            self.repo.set_plugin_settings(new_settings)

    def test_get_plugin_settings_with_info(self):
        # add a plugin into it
        self.repo.plugins.add(self.plugin)
        self.repo.save()

        settings = self.repo.get_plugin_settings_with_info()
        assert settings == {
            'repository': reverse('api:repository-detail',
                                  args=(self.repo.pk,)),
            'plugins': [
                {
                    'name': 'testplugin',
                    'title': 'Testing',
                    'plugin_category': 'test',
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
                }
            ]
        }
