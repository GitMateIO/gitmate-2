from django.contrib.postgres import fields as psql_fields
from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    keywords = psql_fields.JSONField(
        help_text='Comma seperated keywords (values) triggering labels (keys) '
                  'to be set; e.g. type/bug: bug, crash.',
        default=dict)

    label_texts_as_keywords = models.BooleanField(
        default=False,
        help_text='Apply labels if they are mentioned in the issue body '
                  'automatically.')
