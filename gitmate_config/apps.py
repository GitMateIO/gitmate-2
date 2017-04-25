from django.apps import AppConfig
from django.conf import settings


class GitmateConfigConfig(AppConfig):
    name = 'gitmate_config'
    verbose_name = 'Configuration'
    description = 'Provides a REST API for configuring GitMate.'

    def ready(self):
        import gitmate_config.signals
