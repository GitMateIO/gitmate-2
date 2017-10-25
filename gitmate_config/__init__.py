from enum import Enum

from IGitt.GitHub import GitHubToken
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab import GitLabPrivateToken
from IGitt.Interfaces import Token


default_app_config = 'gitmate_config.apps.GitmateConfigConfig'


class GitmateActions(Enum):
    """
    An enum to hold different actions related to gitmate.
    """
    PLUGIN_ACTIVATED = 'plugin_activated'
    PLUGIN_DEACTIVATED = 'plugin_deactivated'


class Providers(Enum):
    GITHUB = 'github'
    GITLAB = 'gitlab'

    def get_token(self, raw_token) -> Token:
        """
        Returns appropriate Token object for the Provider.

        :param raw_token: The token string
        :return: IGitt Token object
        """
        if self.value == 'github':
            return GitHubToken(raw_token)
        elif self.value == 'gitlab':
            return GitLabOAuthToken(raw_token)

    def get_private_token(self, raw_token) -> Token:
        """
        Returns appropriate private Token object for the provider.

        :param raw_token: The token string
        :return: IGitt Token object
        """
        if self.value == 'github':
            return GitHubToken(raw_token)
        elif self.value == 'gitlab':
            return GitLabPrivateToken(raw_token)
