from django.conf import settings
from django.core.management.base import BaseCommand

from gitmate_config.models import Plugin


class Command(BaseCommand):
    help = """
    Update database with all configured GitMate plugins.
    """

    def handle(self, *args, **options):
        for name in settings.GITMATE_PLUGINS:
            try:
                plugin = Plugin.objects.get(name=name)
            except Plugin.DoesNotExist:
                plugin = Plugin(name=name)
            # check importability
            plugin.import_module()
            plugin.save()
