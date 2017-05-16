from django.apps import AppConfig


class GitmateBugSpotterConfig(AppConfig):
    name = 'gitmate_bug_spotter'
    verbose_name = 'PR bug spotter'
    description = 'Searches for files in a newly created PR that are likely'\
                  'sources for bugs and automatically labels them.'
