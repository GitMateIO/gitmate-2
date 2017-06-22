from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.OneToOneField(
        Repository, on_delete=models.CASCADE,
        related_name='gitmate_bug_spotter_repository')
    pattern = models.CharField(
        max_length=100,
        default='(fix(e[sd])?|close[sd]?|resolve[sd]?) #[1-9][0-9]*',
        help_text='The pattern to be compared for spotting bugs.')
    hotspot_label = models.CharField(
        max_length=25,
        default='review carefully!',
        help_text='The label to be used to identify possible bugs.')

    class Meta:
        verbose_name_plural = 'settings'
