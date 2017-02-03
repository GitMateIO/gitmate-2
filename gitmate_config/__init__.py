from enum import Enum


default_app_config = 'gitmate_config.apps.GitmateConfigConfig'


class Providers(Enum):
    GITHUB = 'github'
    GITLAB = 'gitlab'
