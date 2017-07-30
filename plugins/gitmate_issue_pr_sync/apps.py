from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateIssuePrSyncConfig(AppConfig):
    name = 'plugins.gitmate_issue_pr_sync'
    verbose_name = 'Links issue components to related merge request'
    plugin_category = PluginCategory.PULLS
    description = ('Links assignees and labels from issues referenced in a '
                   'merge request with the merge request itself.')
