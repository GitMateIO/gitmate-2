from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    autorespond_text = models.TextField(
        max_length=2500,
        help_text='Text to be commented, upon opening pull request.')
