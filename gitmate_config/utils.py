from typing import Optional

from IGitt.GitHub.GitHub import GitHub
from IGitt.GitLab.GitLab import GitLab
from IGitt.Interfaces.User import User as IGittUser
from django.contrib.auth.models import User
from django.db.models import QuerySet
from social_django.models import UserSocialAuth

from .enums import Providers
from .models import Organization
from .models import Repository


def get_user_if_exists(igitt_user: IGittUser) -> Optional[User]:
    """
    Retrieves matching User from the database, if it exists.
    """
    try:
        return UserSocialAuth.objects.get(provider=igitt_user.hoster,
                                          uid=igitt_user.identifier).user
    except UserSocialAuth.DoesNotExist:
        return None


def divert_access_to_repos(repos: QuerySet(Repository), user: User):
    """
    Hands over the operating user access from one administrator to the next one
    for a repository.

    :param repos:   The list of repositories.
    :param user:    The user whose access is to be diverted.
    """
    for repo in repos.filter(user=user):
        if repo.admins.count() > 1:
            repo.admins.remove(user)
            repo.user = repo.admins.first()
            repo.save()


def divert_access_to_orgs(orgs: QuerySet(Organization), user: User):
    """
    Hands over the operating user access from one administrator to the next one
    for an organization.

    :param orgs:   The list of organizations.
    :param user:    The user whose access is to be diverted.
    """
    for org in orgs.filter(primary_user=user):
        if org.admins.count() > 1:
            org.admins.remove(user)
            org.primary_user = org.admins.first()
            org.save()


class GitMateUser:
    hoster = {
        Providers.GITHUB.value: GitHub,
        Providers.GITLAB.value: GitLab
    }

    def __init__(self, user):
        """
        :param user: ``User`` object of the user, this GitMateUser represents.
        """
        self.user = user

    def get_token(self, provider):
        """
        :param provider: ``Provider`` object whose token is needed.
        """
        raw_token = self.user.social_auth.get(
            provider=provider.value).extra_data['access_token']
        return provider.get_token(raw_token)

    def get_hoster(self, provider):
        return self.hoster[provider.value](self.get_token(provider))

    def master_repos(self, provider):
        hoster = self.get_hoster(provider)
        return hoster.master_repositories
