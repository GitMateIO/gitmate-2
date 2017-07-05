from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateBugSpotterConfig(AppConfig):
    name = 'gitmate_bug_spotter'
    verbose_name = 'PR bug spotter'
    plugin_category = PluginCategory.ANALYSIS.value
    description = 'Sets a label on new pull request if their likelyhood of '\
                  'introducing bugs is high. The analysis calculates a risk '\
                  "for every file, based on it's git history."
