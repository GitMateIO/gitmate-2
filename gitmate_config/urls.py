from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import PluginSettingsView
from .views import RepositoryViewSet
from .views import UserDetailsView

router = DefaultRouter()
router.register(r'repos', RepositoryViewSet, base_name='repository')

urlpatterns = [
    url(r'^me/', UserDetailsView.as_view(), name='user-details'),
    url(r'^settings/?', PluginSettingsView.as_view()),
]

urlpatterns += router.urls
