from os import makedirs

from importlib import import_module

from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand


class Command(TemplateCommand):
    help = """
    Creates a Gitmate plugin directory structure for the given"
    plugin name in the current directory.
    """

    missing_args_message = 'You must provide a plugin name.'

    def handle(self, **options):
        short_plugin_name = options.pop('name')
        plugin_name = 'gitmate_' + short_plugin_name

        options['plugin_name'] = plugin_name
        options['short_plugin_name'] = short_plugin_name
        target = 'plugins/' + plugin_name

        # Change the template directory.
        options['template'] = 'gitmate_config/templates/plugin'

        self.validate_name(plugin_name, 'plugin')

        # Check that the plugin_name cannot be imported.
        try:
            import_module('plugins.' + plugin_name)
        except ImportError:
            # make a new directory for the plugin
            makedirs(target, exist_ok=True)
            pass
        else:
            raise CommandError(
                '%r conflicts with the name of an existing Python module and '
                'cannot be used as an plugin name. Please try another name.'
                % plugin_name
            )

        super().handle(
            'plugin', plugin_name, target, **options)
