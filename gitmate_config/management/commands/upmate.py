from django.conf import settings
from django.core.management.base import BaseCommand

from gitmate_config.models import Plugin


class Command(BaseCommand):
    help = """
    Update database with all configured GitMate plugins.
    """

    def handle(self, *args, **options):
        for name in settings.GITMATE_PLUGINS:
            # check importability
            plugin, _ = Plugin.objects.get_or_create(name=name)
            plugin.import_module()
            self.stdout.write(self.style.SUCCESS(
                'Plugin updated successfully: "%s"' % name))
