from django.conf import settings
from django.core.management.base import BaseCommand

from gitmate_config.models import Plugin
from gitmate_config.models import Repository


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
            module = plugin.import_module()
            plugin.save()
            for repo in Repository.objects.all():
                defaults = module.models.Settings(repo=repo)
                defaults.save()
            self.stdout.write(self.style.SUCCESS(
                'Plugin updated successfully: "%s"' % name))
