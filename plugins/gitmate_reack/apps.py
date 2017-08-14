from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateReackConfig(AppConfig):
    name = 'plugins.gitmate_reack'
    verbose_name = '' # Add something verbose here
    plugin_category = PluginCategory.PULLS # Add plugin category here
    # Valid plugin categories are PULLS, ISSUE and ANALYSIS
    description = '' # Add description here
