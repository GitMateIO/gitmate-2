from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateRebaserConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_rebaser'
    verbose_name = 'Perform a merge, fastforward or rebase when asked for'
    plugin_category = PluginCategory.PULLS
    description = ('Automatically performs a merge, fastforward or rebase on a'
                   'pull request when someone adds a comment with the keywords'
                   '<tt>rebase</tt>, <tt>merge</tt> or <tt>fastforward</tt> '
                   'mentioning the authorized username.'
                   '<br>Example comment:<br><br><tt>"@gitmate-bot rebase"'
                   '</tt>')
