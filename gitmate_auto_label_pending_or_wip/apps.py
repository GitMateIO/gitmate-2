from django.apps import AppConfig


class GitmateAutoLabelPendingOrWipConfig(AppConfig):
    name = 'gitmate_auto_label_pending_or_wip'
    verbose_name = 'PR Autolabelling'
    description = 'Marks PRs/MRs WIP or pending review automatically on push.'
