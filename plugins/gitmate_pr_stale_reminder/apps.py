from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmatePrStaleReminderConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_pr_stale_reminder'
    verbose_name = 'Label inactive pull requests'
    plugin_category = PluginCategory.PULLS
    description = ('Assigns a label to pull requests that have not been '
                   'updated for a certain amount of time.')
