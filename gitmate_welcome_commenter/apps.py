from django.apps import AppConfig


class GitmateWelcomeCommenterConfig(AppConfig):
    name = 'gitmate_welcome_commenter'
    verbose_name = 'PR Autoresponding'
    plugin_category = 'pull_request'
    description = 'Posts a comment in every new pull requests that is opened '\
                  'in this repository.'
