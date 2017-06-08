from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='welcome_commentor_repository')
    autorespond_text = models.TextField(
        max_length=2500,
        help_text='Text to be commented, upon opening pull request.')
