from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateRebaserConfig(AppConfig):
    name = 'plugins.gitmate_rebaser'
    verbose_name = 'Rebase a pull request when commented upon'
    plugin_category = PluginCategory.PULLS
    description = ('Automatically rebases a pull request when someone adds a'
                   'comment with the keyword <tt>rebase</tt> mentioning the '
                   'authorized username.<br>Example comment:<br><br>'
                   '<tt>"@gitmate-bot rebase"</tt>')
