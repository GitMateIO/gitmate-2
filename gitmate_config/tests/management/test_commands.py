from inspect import ismodule
from shutil import rmtree

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from gitmate_config.models import Plugin
from gitmate_config.tests.test_base import GitmateTestCase


class TestCommands(GitmateTestCase):
    def setUp(self):
        super().setUp(upmate=False)

    def test_upmate(self):
        # before calling upmate no plugins should be registered
        self.assertFalse(Plugin.objects.all().exists())
        call_command('upmate')
        # after calling all plugins should be present
        plugins = Plugin.objects.all()
        self.assertEqual(len(plugins), len(settings.GITMATE_PLUGINS))

        testplugin = plugins.get(name='testplugin')
        self.assertEqual(testplugin.name, 'testplugin')

        testplugin_module = testplugin.import_module()
        self.assertTrue(ismodule(testplugin_module))
        self.assertEqual(testplugin_module.__name__,
                         'plugins.gitmate_testplugin')

        call_command('upmate')
        self.repo.plugins.add(testplugin)

        self.assertEqual(self.repo.get_plugin_settings(), {
            'example_bool_setting': True,
            'example_char_setting': 'example',
        })

    def test_startplugin(self):
        # pre existent plugin match
        with pytest.raises(CommandError):
            call_command('startplugin', 'testplugin')

        call_command('startplugin', 'star_wars')
        rmtree('gitmate_star_wars')
