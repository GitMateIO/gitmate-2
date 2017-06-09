from django.apps import AppConfig


class GitmateBugSpotterConfig(AppConfig):
    name = 'gitmate_bug_spotter'
    verbose_name = 'PR bug spotter'
    description = 'Sets a label on new pull request if their likelyhood of '\
                  'introducing bugs is high. The analysis calculates a risk '\
                  "for every file, based on it's git history."
