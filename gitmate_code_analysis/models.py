from django.contrib.postgres import fields as psql_fields
from django.db import models
from IGitt.Interfaces.CommitStatus import Status

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
    status = models.CharField(choices=[(e.name, e.name) for e in Status],
                              default=Status.RUNNING.name,
                              max_length=10)
    results = psql_fields.JSONField(default=None, null=True)

    def __str__(self):  # pragma: no cover
        return '{}@{}'.format(self.repo.full_name, self.sha)

    class Meta:
        unique_together = ('repo', 'sha')
        verbose_name = 'result'
        verbose_name_plural = 'results'
