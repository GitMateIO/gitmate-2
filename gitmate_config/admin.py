from django.contrib import admin

from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_config.models import Organization
from gitmate_config.models import Installation
from gitmate_config.utils import register_all_setting_models


register_all_setting_models()
admin.site.register(Organization)
admin.site.register(Plugin)
admin.site.register(Repository)
admin.site.register(Installation)
