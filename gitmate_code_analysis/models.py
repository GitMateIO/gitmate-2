from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE,
        related_name='gitmate_code_analysis_repository')
    pr_based_analysis = models.BooleanField(
        default=True,
        help_text='Analyze full pull requests and not commit by commit'
    )
