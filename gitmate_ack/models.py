from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='gitmate_ack_repository')
    ack_strs = models.TextField(
        default='ack',
        help_text='Phrases that will be recognized as ack commands.')
    unack_strs = models.TextField(
        default='unack',
        help_text='Phrases that will be recognized as unack commands.')
