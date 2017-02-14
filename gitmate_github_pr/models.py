from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.ForeignKey(
        Repository, on_delete=models.CASCADE,
        related_name="github_pr_repository")
    autorespond_active = models.BooleanField(default=False)
    autorespond_text = models.TextField(max_length=2500)
