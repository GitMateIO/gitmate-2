from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateApproverConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_approver'
    verbose_name = 'Set label on approval'
    plugin_category = PluginCategory.PULLS
    description = ('Adds a label to a pull requests once the CI passes and '
                   'all required manual approvals are given.')
