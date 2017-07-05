from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateIssueLabellerConfig(AppConfig):
    name = 'gitmate_issue_labeller'
    verbose_name = 'Issue Autolabeller'
    plugin_category = PluginCategory.ISSUE.value
    description = 'Sets labels on newly created issues based on keywords.'
