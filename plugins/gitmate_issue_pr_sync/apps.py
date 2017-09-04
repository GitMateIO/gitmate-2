from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateIssuePrSyncConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_issue_pr_sync'
    verbose_name = 'Synchronize issue labels to related PRs'
    plugin_category = PluginCategory.PULLS
    description = ('Synchronizes labels from issues referenced in a Pull '
                   'Request to the Pull Request.')
