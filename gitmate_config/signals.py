from django.db.models.signals import post_save
from django.dispatch import receiver

from gitmate_config.models import Plugin
from gitmate_config.models import Repository


@receiver(post_save, sender=Repository, dispatch_uid='init_plugin_settings')
def initialize_plugin_settings(sender, instance, created, **kwargs):
    """
    Initializes default settings for each repository.
    """

    if created is True:
        plugins = Plugin.objects.all()
        for plugin in plugins:
            module = plugin.import_module()
            defaults = module.models.Settings(repo=instance)
            defaults.save()
