from gitmate.utils import GitmatePluginConfig
from gitmate.enums import PluginCategory


class GitmateIssueLabellerConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_issue_labeller'
    verbose_name = 'Assign labels based on keywords'
    plugin_category = PluginCategory.ISSUE
    description = 'Assign all labels to an issue that appear in the issue ' \
                  'description or based on keywords'
