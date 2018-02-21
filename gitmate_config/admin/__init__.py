from django.contrib import admin

from gitmate_config.admin.utils import register_all_setting_models
from gitmate_config.admin.utils import DisplayAllAdmin
from gitmate_config.models import Repository
from gitmate_config.models import Organization
from gitmate_config.models import Installation


register_all_setting_models()
admin.site.register(Organization, DisplayAllAdmin)
admin.site.register(Repository, DisplayAllAdmin)
admin.site.register(Installation, DisplayAllAdmin)
