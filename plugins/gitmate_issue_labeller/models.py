from django.contrib.postgres import fields as psql_fields
from django.db import models

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    keywords = psql_fields.JSONField(
        help_text='Comma seperated keywords (values) triggering labels (keys) '
                  'to be set; e.g. type/bug: bug, crash.',
        default={}
    )
