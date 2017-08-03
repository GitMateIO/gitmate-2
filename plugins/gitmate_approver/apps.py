from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateApproverConfig(AppConfig):
    name = 'plugins.gitmate_approver'
    verbose_name = 'Add approved label on passing all tests'
    plugin_category = PluginCategory.PULLS
    description = ('Checks the head commit of a merge request on status '
                   'change and labels it as approved.')
