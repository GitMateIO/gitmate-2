from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateWelcomeCommenterConfig(AppConfig):
    name = 'gitmate_welcome_commenter'
    verbose_name = 'PR Autoresponding'
    plugin_category = PluginCategory.PULLS
    description = 'Posts a comment in every new pull requests that is opened '\
                  'in this repository.'
