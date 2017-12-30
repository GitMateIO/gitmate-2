from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    enable_rebase = models.BooleanField(
        default=True,
        help_text='Rebase on default branch (git rebase).')
    enable_merge = models.BooleanField(
        default=False,
        help_text='Merge to default branch (git merge --no-ff).')
    enable_fastforward = models.BooleanField(
        default=False,
        help_text='Fast forward default branch (git merge --ff-only)')
