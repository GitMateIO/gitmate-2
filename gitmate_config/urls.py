from rest_framework.routers import DefaultRouter

from .views import PluginSettingsViewSet
from .views import RepositoryViewSet
from .views import UserViewSet

from os import path
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url

router = DefaultRouter()
router.register(r'repos', RepositoryViewSet, base_name='repository')
router.register(r'plugins', PluginSettingsViewSet, base_name='settings')
router.register(r'users', UserViewSet, base_name='users')

plugin_routes = [
    url(f'^plugin/{plugin}', include(f'plugins.gitmate_{plugin}.urls'))
    for plugin in settings.GITMATE_PLUGINS
    if path.isfile(f'plugins/gitmate_{plugin}/urls.py')
]

urlpatterns = router.urls
urlpatterns.extend(plugin_routes)
