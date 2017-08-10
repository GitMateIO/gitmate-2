from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    pr_expire_limit = models.IntegerField(
        default=7,
        help_text='No. of days after which a pull request is labelled stale')
    stale_label = models.CharField(
        default='status/STALE',
        max_length=100,
        help_text='Label to use for a marking stale pull requests')
