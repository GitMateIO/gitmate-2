from django.apps import AppConfig


class GitmateAutoLabelPendingOrWipConfig(AppConfig):
    name = 'gitmate_auto_label_pending_or_wip'
    verbose_name = 'PR Autolabelling'
    description = 'Sets labels on new and updated pull requests to '\
                  'differentiate those that are WIP from those that '\
                  'are ready for review.'
