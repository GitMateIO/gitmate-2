from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateBugSpotterConfig(AppConfig):
    name = 'plugins.gitmate_bug_spotter'
    verbose_name = 'Assign label based on risk'
    plugin_category = PluginCategory.PULLS
    description = 'Sets a label on new pull request if their likelyhood of '\
                  'introducing bugs is high. The analysis calculates a risk '\
                  "for every file, based on it's git history."
