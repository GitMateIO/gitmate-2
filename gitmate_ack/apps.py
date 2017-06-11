from django.apps import AppConfig

class GitmateAckConfig(AppConfig):
    name = 'gitmate_ack'
    verbose_name = 'Commit Acknowledger'
    description = 'Acknowledge/Unacknowledge commits in a PR'\
                  'based on keywords in comment.'
