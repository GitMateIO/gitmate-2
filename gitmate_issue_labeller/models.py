from django.contrib.postgres import fields as psql_fields
from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE,
        related_name='gitmate_issue_labeller_repository')
    blacklisted_labels = psql_fields.ArrayField(
        models.CharField(max_length=20, default=''),
        blank=False,
        help_text='The labels to be avoided on issues.',
        default=['invalid', 'duplicate', 'bounty'])
