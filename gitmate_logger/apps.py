from django.apps import AppConfig
from django.conf import settings
from django.core.signals import got_request_exception


class GitmateLoggerConfig(AppConfig):
    name = 'gitmate_logger'

    def ready(self):
        # Don't move to module code! Apps aren't loaded yet.
        from gitmate_logger.signals import LoggingExceptionHandler

        if not settings.DEBUG:
            got_request_exception.connect(
                LoggingExceptionHandler.create_from_exception)
