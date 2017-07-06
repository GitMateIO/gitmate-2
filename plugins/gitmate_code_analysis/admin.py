from django.contrib import admin

from .models import Settings, AnalysisResults

admin.site.register(Settings)
admin.site.register(AnalysisResults)
