from django.apps import AppConfig


class CoafileBotConfig(AppConfig):
    name = 'coafile_bot'

    def ready(self):
        import coafile_bot.responders as _
