from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateAutoLabelPendingOrWipConfig(AppConfig):
    name = 'plugins.gitmate_auto_label_pending_or_wip'
    verbose_name = 'Assign label based on review state'
    plugin_category = PluginCategory.PULLS
    description = 'Sets labels on new and updated pull requests to '\
                  'differentiate those that are WIP from those that '\
                  'are ready for review.'
