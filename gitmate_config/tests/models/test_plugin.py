from inspect import ismodule

from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import IntegrityError
from django.db import models
from django.http import Http404
from django.test import TransactionTestCase
import pytest

from gitmate_config.models import Plugin
from gitmate_config.models import Repository


@pytest.mark.django_db(transaction=False)
class TestPlugin(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            password="top_secret",
            first_name="John",
            last_name="Appleseed"
        )
        self.repo = Repository(
            user=self.user, full_name='test', provider='example')
        self.repo.save()
        self.plugin = Plugin(name="testplugin")
        self.plugin_module = self.plugin.import_module()
        self.plugin.save()
        self.settings = self.plugin_module.models.Settings()
        self.settings.repo = self.repo
        self.settings.save()

    def test_name(self):
        plugin = Plugin()
        # check default value
        assert plugin.name is None
        # and that field validation fails on empty name
        with pytest.raises(ValidationError):
            plugin.full_clean()
        # trying to save a None name should raise a database error
        with pytest.raises(IntegrityError):
            plugin.save()
        # also empty string must no be allowed
        plugin.name = ''
        # whereby saving empty name strings to database unfortunately works,
        # so never forget to call .full_clean() before custom .save() calls
        with pytest.raises(ValidationError):
            plugin.full_clean()
        plugin.name = 'test'
        plugin.full_clean()

    def test_active(self):
        plugin = Plugin()
        # just check default value
        assert not plugin.active

    def test__str__(self):
        plugin = Plugin(name='test')
        assert str(plugin) == 'test'

    def test_import_module(self):
        plugin = Plugin(name='testplugin')
        # import_module should try to import gitmate_{plugin.name}
        module = plugin.import_module()
        assert ismodule(module)
        assert module.__name__ == 'gitmate_testplugin'

    def test_set_plugin_settings(self):
        new_settings = {
            'example_bool_setting': False,
            'example_char_setting': "hello"
        }
        self.plugin.set_settings_for_repo(self.repo, new_settings)

        modified_settings = self.plugin.get_plugin_settings(self.repo)
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == "hello"

    def test_set_all_plugin_settings(self):
        old_settings = Plugin.get_all_settings(self.repo)

        # No proper plugin name
        new_settings = [{
            'status': 'active',
            'settings': {}
        }]
        with pytest.raises(Http404):
            Plugin.set_all_settings_for_repo(self.repo, new_settings)
        modified_settings = Plugin.get_all_settings(self.repo)
        assert modified_settings == old_settings

        # No status setting
        new_settings = [{
            'name': 'testplugin',
            'settings': {}
        }]
        Plugin.set_all_settings_for_repo(self.repo, new_settings)
        modified_settings = Plugin.get_all_settings(self.repo)
        assert modified_settings == old_settings

        # Undefined plugin
        new_settings = [{
            'name': 'undefinedplugin'
        }]
        with pytest.raises(Http404):
            Plugin.set_all_settings_for_repo(self.repo, new_settings)
        modified_settings = Plugin.get_all_settings(self.repo)
        assert modified_settings == old_settings

        # Successful set change activeness
        new_settings = [{
            'name': 'testplugin',
            'status': 'inactive',
        }]
        Plugin.set_all_settings_for_repo(self.repo, new_settings)
        assert self.plugin.active is False

        # Successful set
        new_settings = [{
            'name': 'testplugin',
            'status': 'active',
            'settings': {
                'example_bool_setting': False,
                'example_char_setting': "hello"
            }
        }]
        Plugin.set_all_settings_for_repo(self.repo, new_settings)

        modified_settings = Plugin.get_all_settings(self.repo)
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == "hello"

    def test_get_plugin_settings(self):
        settings = Plugin.get_all_settings(self.repo)
        assert settings == {'example_bool_setting': True,
                            'example_char_setting': 'example'}

    def test_get_plugin_settings_by_user(self):
        settings = Plugin.get_all_settings_by_user(self.user)
        assert settings == [{
            "repository": self.repo.full_name,
            "plugins": {
                "testplugin": {
                    "status": "inactive",
                    "settings": {
                        "example_bool_setting": {
                            "description": "An example Bool setting",
                            "value": True,
                            "type": "BooleanField"
                        },
                        "example_char_setting": {
                            "description": "An example Char setting",
                            "value": "example",
                            "type": "CharField"
                        }
                    }
                }
            }
        }]

    def test_get_plugin_settings_by_repo(self):
        settings = Plugin.get_all_settings_by_repo(self.repo)
        assert settings == {
            "repository": self.repo.full_name,
            "plugins": {
                "testplugin": {
                    "status": "inactive",
                    "settings": {
                        "example_bool_setting": {
                            "description": "An example Bool setting",
                            "value": True,
                            "type": "BooleanField"
                        },
                        "example_char_setting": {
                            "description": "An example Char setting",
                            "value": "example",
                            "type": "CharField"
                        }
                    }
                }
            }
        }
