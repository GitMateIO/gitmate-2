from rest_framework.routers import DefaultRouter

from .views import PluginSettingsViewSet
from .views import RepositoryViewSet
from .views import UserViewSet

router = DefaultRouter()
router.register(r'repos', RepositoryViewSet, base_name='repository')
router.register(r'plugins', PluginSettingsViewSet, base_name='settings')
router.register(r'users', UserViewSet, base_name='users')

urlpatterns = router.urls
