from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    list_duplicates = models.BooleanField(
        default=True,
        help_text='Link duplicate issues in a comment')
    list_similar = models.BooleanField(
        default=True,
        help_text='Link similar issues in a comment')
