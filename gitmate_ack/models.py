from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    ack_strs = models.CharField(
        default='ack',
        max_length=100,
        help_text='Phrases that will be recognized as ack commands.')
    unack_strs = models.CharField(
        default='unack',
        max_length=100,
        help_text='Phrases that will be recognized as unack commands.')
