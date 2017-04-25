from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import IntegrityError
from django.db import models
from django.http import Http404
from django.test import TransactionTestCase
import pytest
from rest_framework.reverse import reverse

from gitmate_config.models import Plugin
from gitmate_config.models import Repository


@pytest.mark.django_db(transaction=False)
class TestRepository(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            email='john.appleseed@example.com',
            password='top_secret',
            first_name='John',
            last_name='Appleseed'
        )
        self.plugin = Plugin(name='testplugin')
        self.plugin_module = self.plugin.import_module()
        self.plugin.save()
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
        repo = Repository(user=self.user,
                          full_name=self.full_name,
                          provider=self.provider)
        repo.save()  # id creation required before many-many relationship

        # add a plugin into it
        repo.plugins.add(self.plugin)
        repo.save()

        old_settings = repo.get_plugin_settings()

        # No proper plugin name
        new_settings = [{
            'active': True,
            'settings': {}
        }]
        with pytest.raises(Http404):
            repo.set_plugin_settings(new_settings)
        modified_settings = repo.get_plugin_settings()
        assert modified_settings == old_settings

        # No status setting
        new_settings = [{
            'name': 'testplugin',
            'settings': {}
        }]
        repo.set_plugin_settings(new_settings)
        modified_settings = repo.get_plugin_settings()
        assert modified_settings == old_settings

        # Undefined plugin
        new_settings = [{
            'name': 'undefinedplugin'
        }]
        with pytest.raises(Http404):
            repo.set_plugin_settings(new_settings)
        modified_settings = repo.get_plugin_settings()
        assert modified_settings == old_settings

        # Remove all plugins
        new_settings = [{
            'name': 'testplugin',
            'active': False,
        }]
        repo.set_plugin_settings(new_settings)
        modified_settings = repo.get_plugin_settings()
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
        repo.set_plugin_settings(new_settings)

        modified_settings = repo.get_plugin_settings()
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == 'hello'

    def test_get_plugin_settings_with_info(self):
        # create a fake repo
        repo = Repository(user=self.user,
                          full_name=self.full_name,
                          provider=self.provider)
        repo.save()  # id creation required before many-many relationship

        # add a plugin into it
        repo.plugins.add(self.plugin)
        repo.save()

        settings = repo.get_plugin_settings_with_info()
        assert settings == {
            'repository': reverse('api:repository-detail',
                                  args=(repo.pk,)),
            'plugins': [
                {
                    'name': 'testplugin',
                    'title': 'Testing',
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
