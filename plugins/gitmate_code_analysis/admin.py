from django.contrib import admin

from gitmate_code_analysis.models import Settings, AnalysisResults

admin.site.register(Settings)
admin.site.register(AnalysisResults)
