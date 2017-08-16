from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    size_scheme = models.CharField(
        default='size/{size}',
        max_length=100,
        help_text='Label scheme to use, use {size} as placeholder')
