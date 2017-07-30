from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateIssuePrSyncConfig(AppConfig):
    name = 'plugins.gitmate_issue_pr_sync'
    verbose_name = ('Copy labels and assignees from issues referenced in '
                    'merge requests onto the merge requests')
    plugin_category = PluginCategory.PULLS
    description = ('Copies assignees and labels from issues referenced in a '
                   'PR to the PR and maintains a unidirectional sync between '
                   'referenced issues and PRs.')
