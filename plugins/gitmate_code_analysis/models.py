from django.contrib.postgres import fields as psql_fields
from django.db import models

from gitmate_config.models import Repository, SettingsBase


class Settings(SettingsBase):
    pr_based_analysis = models.BooleanField(
        default=True,
        help_text='Analyze full pull requests and not commit by commit'
    )


class AnalysisResults(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE,
        related_name='analysis_result_repository')
    sha = models.CharField(default=None, max_length=40)
    results = psql_fields.JSONField()

    def __str__(self):  # pragma: no cover
        return '{}@{}'.format(self.repo.full_name, self.sha)

    class Meta:
        unique_together = ('repo', 'sha')
        verbose_name = 'result'
        verbose_name_plural = 'results'
