from gitmate.utils import GitmatePluginConfig
from gitmate.enums import PluginCategory


class GitmateApproverConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_approver'
    verbose_name = 'Add approved label on passing all tests'
    plugin_category = PluginCategory.PULLS
    description = ('Checks the head commit of a merge request on status '
                   'change and labels it as approved.')
