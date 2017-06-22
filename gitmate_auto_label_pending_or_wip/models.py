from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='auto_label_pending_or_wip_repository')
    wip_label = models.CharField(
        max_length=25,
        default='process/WIP',
        help_text='The label to be used for marking work in progress.')
    pending_review_label = models.CharField(
        max_length=25,
        default='process/pending_review',
        help_text='The label to be used for marking pending review.')

    class Meta:
        verbose_name_plural = 'settings'
