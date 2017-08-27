from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateSimilarIssuesConfig(AppConfig):
    name = 'plugins.gitmate_similar_issues'
    verbose_name = '' # Add something verbose here
    plugin_category = PluginCategory.PULLS # Add plugin category here
    # Valid plugin categories are PULLS, ISSUE and ANALYSIS
    description = '' # Add description here
