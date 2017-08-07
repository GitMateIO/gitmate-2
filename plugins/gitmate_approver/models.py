from django.contrib.postgres import fields as psql_fields
from django.db import models

from gitmate_config.models import Repository
from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    status_labels = models.CharField(max_length=500,
        default='process/pending_review, process/WIP',
        help_text='Comma seperated labels to be removed from the merge '
                  'request once it has been approved. e.g. process/WIP, '
                  'status/stale, process/pending_review')
    approved_label = models.CharField(max_length=40, default='status/approved')


class MergeRequestModel(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name='approver_mr')
    number = models.IntegerField()
    head_sha = models.CharField(max_length=40, default='')

    @property
    def igitt_pr(self):
        """
        Returns an IGitt MergeRequest instance from the model attributes.
        """
        return self.repo.igitt_repo.get_mr(self.number)

    class Meta:
        unique_together = ('repo', 'number')
