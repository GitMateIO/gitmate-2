from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    enable_rebase = models.BooleanField(
        default=True, help_text='Enables rebase command.')
    enable_merge = models.BooleanField(
        default=False, help_text='Enables merge command.')
    enable_fastforward = models.BooleanField(
        default=False, help_text='Enables fastforward or ff command.')
