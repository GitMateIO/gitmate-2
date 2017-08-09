from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateIssuePrSyncConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_issue_pr_sync'
    verbose_name = 'Synchronize labels from referenced issues'
    plugin_category = PluginCategory.PULLS
    description = ('Assigns all labels from an issue to a pull request that '
                   'referenced the issue. Changes to the labels of the issue '
                   'get reflected in the pull request.')
