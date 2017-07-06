from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateTestpluginConfig(AppConfig):
    name = 'gitmate_testplugin'
    verbose_name = 'Testing'
    plugin_category = PluginCategory.ISSUE
    description = 'A simple plugin used for testing. Smile :)'
