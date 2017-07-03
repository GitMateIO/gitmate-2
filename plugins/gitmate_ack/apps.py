from django.apps import AppConfig

class GitmateAckConfig(AppConfig):
    name = 'gitmate_ack'
    verbose_name = 'Commit Acknowledger'
    description = ('Acknowledge/Unacknowledge commits in a PR based on '
                   'keywords in a PR comment. Acknowledgements have high '
                   'priority. Providing same keyword for both will result in'
                   'acknowledgement action. You can provide multiple '
                   'keywords separated with a comma.')
