from django.apps import AppConfig


class GitmateTestpluginConfig(AppConfig):
    name = 'gitmate_testplugin'
    verbose_name = 'Testing'
    plugin_category = 'test'
    description = 'A simple plugin used for testing. Smile :)'
