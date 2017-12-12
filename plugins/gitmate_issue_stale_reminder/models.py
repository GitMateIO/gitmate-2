from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    issue_expire_limit = models.IntegerField(
        default=30,
        help_text='No. of days after which an issue is considered stale')
    stale_label = models.CharField(
        default='status/STALE',
        max_length=100,
        help_text='Label to use for a marking stale issues')
    unassign = models.BooleanField(
        default=True,
        help_text='Unassign assignees if an issue goes stale',
    )
