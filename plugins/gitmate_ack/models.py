from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    ack_strs = models.CharField(
        default='ack, reack',
        max_length=100,
        help_text='Keywords for acknowledging commits, comma separated')
    unack_strs = models.CharField(
        default='unack',
        max_length=100,
        help_text='Keywords for unacknowledging commits, comma separated')
