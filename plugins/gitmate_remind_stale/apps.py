from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateRemindStaleConfig(AppConfig):
    name = 'plugins.gitmate_remind_stale'
    verbose_name = 'Label inactive PRs and issues as stale'
    plugin_category = PluginCategory.PULLS
    description = ('Adds a stale label in every pull request and issue which '
                   'remains inactive for a specified period of time.')
