from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    wip_label = models.CharField(
        max_length=25,
        default='process/WIP',
        help_text='Label for pull requests that are work in progress')
    pending_review_label = models.CharField(
        max_length=25,
        default='process/pending_review',
        help_text='Label for pull requests that need review')
