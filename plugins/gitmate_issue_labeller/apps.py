from django.apps import AppConfig


class GitmateIssueLabellerConfig(AppConfig):
    name = 'gitmate_issue_labeller'
    verbose_name = 'Issue Autolabeller'
    description = 'Sets labels on newly created issues based on keywords.'
