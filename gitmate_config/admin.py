from django.contrib import admin

from gitmate_config.models import Plugin, Repository, Customer, Organization

admin.site.register(Customer)
admin.site.register(Organization)
admin.site.register(Plugin)
admin.site.register(Repository)
