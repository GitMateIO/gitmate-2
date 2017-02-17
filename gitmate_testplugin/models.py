from django.db import models

from gitmate_config.models import Repository


class Settings(models.Model):
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE,
                             related_name='gitmate_testplugin_repository')
    example_char_setting = models.CharField(
        max_length=25, default='example', help_text='An example Char setting')
    example_bool_setting = models.BooleanField(
        default=True, help_text='An example Bool setting')
