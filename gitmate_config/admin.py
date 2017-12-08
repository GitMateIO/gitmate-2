from django.contrib import admin

from gitmate_config.models import Plugin, Repository, Organization, Installation


admin.site.register(Organization)
admin.site.register(Plugin)
admin.site.register(Repository)
admin.site.register(Installation)
