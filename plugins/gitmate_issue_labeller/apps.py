from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateIssueLabellerConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_issue_labeller'
    verbose_name = 'Assign mentioned labels'
    plugin_category = PluginCategory.INITIAL
    description = 'Assign all labels to an issue that appear in the issue description'
