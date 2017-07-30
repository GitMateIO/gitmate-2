from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    days = models.IntegerField(
        default=7,
        help_text='No. of days after which a PR or an issue is marked stale')
    stale_label = models.CharField(
        default='status/STALE',
        max_length=100,
        help_text='Label to use for a marking PRs and issues as stale')
