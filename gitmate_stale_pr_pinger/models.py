from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='gitmate_stale_pr_pinger_repository')
    # Add your custom plugin settings here.
