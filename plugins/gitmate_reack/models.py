from django.db import models

from gitmate_config.models import Repository
from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    # Add your custom plugin settings here.
    pass


class CommitModel(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name='reack')
    hash_value = models.CharField(max_length=40)
    status = models.IntegerField()

    class Meta:
        unique_together = ('repo', 'hash_value')
