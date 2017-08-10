from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateIssueStaleReminderConfig(AppConfig):
    name = 'plugins.gitmate_issue_stale_reminder'
    verbose_name = 'Label inactive issues'
    plugin_category = PluginCategory.ISSUE
    description = ('Assigns a label to issues that have not been updated for '
                   'a certain amount of time.')
