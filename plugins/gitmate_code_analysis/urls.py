from django.conf.urls import url

from .views import get_analysis_result

urlpatterns = [
    url(r'^results/$', get_analysis_result, name='result')
]
