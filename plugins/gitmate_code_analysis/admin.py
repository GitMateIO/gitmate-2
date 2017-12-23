from django.contrib import admin

from gitmate_config.admin.utils import DisplayAllAdmin
from .models import AnalysisResults


admin.site.register(AnalysisResults, DisplayAllAdmin)
