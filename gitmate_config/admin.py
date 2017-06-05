from django.contrib import admin

from gitmate_config.models import Plugin, Repository

admin.site.register(Plugin)
admin.site.register(Repository)
