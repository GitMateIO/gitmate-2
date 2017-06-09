from django.apps import AppConfig


class GitmatePrSizeLabellerConfig(AppConfig):
    name = 'gitmate_pr_size_labeller'
    verbose_name = 'PR Size Labelling'
    description = (
        'Sets size labels on new pull requests in this repository'\
        ' (XS/S/M/L/XL/XXL). '\
        'The number of changed lines of code is taken into account as well '\
        'as the number of commits and that of files changed.'
    )
