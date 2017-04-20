from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE,
        related_name='pr_size_labeller_repository')
