from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    pattern = models.CharField(
        max_length=100,
        default='(fix(e[sd])?|close[sd]?|resolve[sd]?) #[1-9][0-9]*',
        help_text='Pattern used on commit messages to identify bug fixes')
    hotspot_label = models.CharField(
        max_length=25,
        default='review carefully!',
        help_text='Label for pull requests with high risk')
