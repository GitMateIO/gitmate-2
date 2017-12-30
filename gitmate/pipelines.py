"""
This module contains the additional social authentication pipelines for
GitMate.
"""
from django.contrib.auth.models import User
from social_core.backends.oauth import BaseOAuth2

from IGitt.GitHub.GitHubUser import GitHubUser
from gitmate.tasks import populate_github_repositories
from gitmate_config.enums import Providers


def populate_repositories(backend: BaseOAuth2, user: User, *args, **kwargs):
    """
    Connects the user to his / her existing installations, if any were made
    prior to GitMate login.
    """
    if backend.name != Providers.GITHUB_APP.value:
        return

    raw_token = user.social_auth.get(provider=backend.name).access_token
    token = Providers(backend.name).get_token(raw_token)
    populate_github_repositories.delay(user, GitHubUser(token))
