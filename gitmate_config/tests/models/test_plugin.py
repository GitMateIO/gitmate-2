from inspect import ismodule

from django.core.validators import ValidationError
import pytest

from gitmate_config.models import Plugin
from gitmate_config.tests.test_base import GitmateTestCase


class TestPlugin(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')

    def test_name(self):
        plugin = Plugin()
        # check default value
        assert plugin.name is None
        # and that field validation fails on empty name
        with pytest.raises(ValidationError):
            plugin.full_clean()
        # trying to save a None name should raise a database error
        with pytest.raises(ValidationError):
            plugin.save()
        # also empty string must no be allowed
        plugin.name = ''
        # whereby saving empty name strings to database unfortunately works,
        # so never forget to call .full_clean() before custom .save() calls
        with pytest.raises(ValidationError):
            plugin.full_clean()
        plugin.name = 'test'
        plugin.full_clean()

    def test__str__(self):
        plugin = Plugin(name='test')
        assert str(plugin) == 'test'

    def test_import_module(self):
        plugin = Plugin(name='testplugin')
        # import_module should try to import gitmate_{plugin.name}
        module = plugin.import_module()
        assert ismodule(module)
        assert module.__name__ == 'plugins.gitmate_testplugin'

    def test_set_settings(self):
        new_settings = {
            'example_bool_setting': False,
            'example_char_setting': 'hello'
        }
        self.plugin.set_settings(self.repo, new_settings)

        modified_settings = self.plugin.get_settings(self.repo)
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == 'hello'

    def test_get_settings(self):
        settings = self.plugin.get_settings(self.repo)
        assert settings == {'example_bool_setting': True,
                            'example_char_setting': 'example'}
