from django.apps import AppConfig
from django.conf import settings


class GitmateConfigConfig(AppConfig):
    name = 'gitmate_config'

    def ready(self):
        import gitmate_config.signals
