from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateSimilarIssuesConfig(AppConfig):
    name = 'plugins.gitmate_similar_issues'
    verbose_name = 'Find similar issues'
    plugin_category = PluginCategory.ISSUE
    # Valid plugin categories are PULLS, ISSUE and ANALYSIS
    description = ('<p>Proposes similar and duplicate issues in a comment when '
                   'an issue is opened.</p>'
                   '<p>In the future, related labels will be set and relevant '
                   'devs pinged</p>')
