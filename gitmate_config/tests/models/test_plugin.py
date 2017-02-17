from inspect import ismodule
from unittest import TestCase

from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import IntegrityError
from django.db import models
import pytest

from gitmate_config.models import Plugin
from gitmate_config.models import Repository


@pytest.mark.django_db(transaction=False)
class TestPlugin(TestCase):

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

    def test_get_plugin_settings(self):
        plugin = Plugin(name='testplugin')
        plugin_module = plugin.import_module()
        plugin.save()
        settings = plugin_module.models.Settings()
        settings.repo = self.repo
        settings.save()

        settings = Plugin.get_all_settings(self.repo)
        assert settings == {'example_bool_setting': True,
                            'example_char_setting': 'example'}

    def test_get_plugin_settings_detailed(self):
        plugin = Plugin(name="testplugin")
        plugin_module = plugin.import_module()
        plugin.save()
        settings = plugin_module.models.Settings()
        settings.repo = self.repo
        settings.save()

        settings = Plugin.get_all_settings_detailed(self.repo)
        assert settings == {
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
