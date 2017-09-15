from django.contrib.postgres import fields as psql_fields

from gitmate_config.models import SettingsBase


class Settings(SettingsBase):
    keywords = psql_fields.JSONField(
        help_text='Comma seperated keywords (values) triggering assignees ('
                  'keys) '
                  'to be set; e.g. sils: bug, crash.',
        default={}
    )
