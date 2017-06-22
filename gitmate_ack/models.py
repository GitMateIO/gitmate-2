from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='gitmate_ack_repository')
    ack_strs = models.CharField(
        default='ack',
        max_length=100,
        help_text='Phrases that will be recognized as ack commands.')
    unack_strs = models.CharField(
        default='unack',
        max_length=100,
        help_text='Phrases that will be recognized as unack commands.')

    class Meta:
        verbose_name_plural = 'settings'
