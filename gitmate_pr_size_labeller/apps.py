from django.apps import AppConfig


class GitmatePrSizeLabellerConfig(AppConfig):
    name = 'gitmate_pr_size_labeller'
    verbose_name = 'PR Size Labelling'
    description = (
        'Marks PRs/MRs with size/{XS|S|M|L|XL|XXL} labels based on the number '
        'of touched LOC, commits, touched files etc.'
    )
