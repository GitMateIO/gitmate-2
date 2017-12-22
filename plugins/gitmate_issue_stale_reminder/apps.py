from gitmate.utils import GitmatePluginConfig
from gitmate.enums import PluginCategory


class GitmateIssueStaleReminderConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_issue_stale_reminder'
    verbose_name = 'Label inactive issues'
    plugin_category = PluginCategory.ISSUE
    description = ('Assigns a label to issues that have not been updated or '
                   'mentioned in a PR for a certain amount of time.')
