from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateIssueLabellerConfig(AppConfig):
    name = 'plugins.gitmate_issue_labeller'
    verbose_name = 'Assign mentioned labels'
    plugin_category = PluginCategory.ISSUE
    description = 'Assign all labels to an issue that appear in the issue description'
