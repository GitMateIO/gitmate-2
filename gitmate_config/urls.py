from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import PluginSettingsViewSet
from .views import RepositoryViewSet
from .views import UserDetailsView

router = DefaultRouter()
router.register(r'repos', RepositoryViewSet, base_name='repository')
router.register(r'plugins', PluginSettingsViewSet, base_name='settings')

urlpatterns = [
    url(r'^me/', UserDetailsView.as_view(), name='user-details'),
]

urlpatterns += router.urls
