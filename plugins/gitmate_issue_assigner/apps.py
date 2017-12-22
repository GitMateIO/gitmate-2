from gitmate.utils import GitmatePluginConfig
from gitmate.enums import PluginCategory


class GitmateIssueAssignerConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_issue_assigner'
    verbose_name = 'Assign mentioned contributors'
    plugin_category = PluginCategory.ISSUE
    description = 'Assign all users to issues based on keywords'
