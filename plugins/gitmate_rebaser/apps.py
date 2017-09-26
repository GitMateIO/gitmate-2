from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateRebaserConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_rebaser'
    verbose_name = 'Rebase a pull request when commented upon'
    plugin_category = PluginCategory.OTHER
    description = ('Automatically rebases a pull request when someone adds a'
                   'comment with the keyword <tt>rebase</tt> mentioning the '
                   'authorized username.<br>Example comment:<br><br>'
                   '<tt>"@gitmate-bot rebase"</tt>')
