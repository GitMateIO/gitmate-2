from django.contrib import admin

from gitmate_config.models import Plugin, Repository, Organization

admin.site.register(Organization)
admin.site.register(Plugin)
admin.site.register(Repository)
