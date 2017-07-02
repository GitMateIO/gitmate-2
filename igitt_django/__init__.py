"""
This module contains the django compatible igitt utilities.
"""
from enum import Enum
from IGitt.GitHub import GitHubToken
from IGitt.GitLab import GitLabOAuthToken


class Providers(Enum):
    """
    A helper class for igitt_django models that contains hoster related data.
    """
    GITHUB = 'github'
    GITLAB = 'gitlab'

    def get_token(self, raw_token):
        """
        Returns appropriate Token object for the Provider.

        :param raw_token: The token string
        :return: IGitt Token object
        """
        if self.value == 'github':
            return GitHubToken(raw_token)
        else:
            return GitLabOAuthToken(raw_token)
