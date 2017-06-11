from django.apps import AppConfig


class CoalaOnlineConfig(AppConfig):
    name = 'coala_online'
    verbose_name = 'API endpoint to run coala and coala-quickstart online'
    description = 'The ``coala_online`` endpoint helps' \
                  'users to run coala-quickstart and coala on their code' \
                  'snippet or on a git repository.'
