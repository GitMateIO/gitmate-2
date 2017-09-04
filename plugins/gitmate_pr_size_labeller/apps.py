from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmatePrSizeLabellerConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_pr_size_labeller'
    verbose_name = 'Assign label based on size'
    plugin_category = PluginCategory.PULLS
    description = (
        'Sets size labels on new pull requests in this repository'\
        ' (XS/S/M/L/XL/XXL). '\
        'The number of changed lines of code is taken into account as well '\
        'as the number of commits and that of files changed.'
    )
