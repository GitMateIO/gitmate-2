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
        plugin_name = 'gitmate_' + options.pop('name')

        # Change the template directory.
        options['template'] = 'gitmate_config/templates/plugin'

        self.validate_name(plugin_name, 'plugin')

        # Check that the plugin_name cannot be imported.
        try:
            import_module(plugin_name)
        except ImportError:
            pass
        else:
            raise CommandError(
                '%r conflicts with the name of an existing Python module and '
                'cannot be used as an plugin name. Please try another name.'
                % plugin_name
            )

        super().handle(
            'plugin', plugin_name, None, **options)
