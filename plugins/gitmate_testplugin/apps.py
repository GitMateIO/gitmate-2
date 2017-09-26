from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateTestpluginConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_testplugin'
    verbose_name = 'Testing'
    plugin_category = PluginCategory.OTHER
    description = 'A simple plugin used for testing. Smile :)'
