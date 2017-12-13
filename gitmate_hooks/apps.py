from django.apps import AppConfig


class GitmateHooksConfig(AppConfig):
    name = 'gitmate_hooks'
    verbose_name = 'GitMate Webhook Utilities'
    description = 'Provides a handling mechanism for incoming webhooks.'

    def ready(self):
        import gitmate_hooks.utils as _
        import gitmate_hooks.responders as _
