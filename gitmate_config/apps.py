from django.apps import AppConfig
from django.conf import settings


class GitmateConfigConfig(AppConfig):
    name = 'gitmate_config'

    def ready(self):
        """
        Update database with all configured plugins.
        """
        from .models import Plugin

        for name in settings.GITMATE_PLUGINS:
            try:
                plugin = Plugin.objects.get(name=name)
            except Plugin.DoesNotExist:
                plugin = Plugin(name=name)
            # check importability
            plugin.import_module()
            plugin.save()
