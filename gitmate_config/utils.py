from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models import QuerySet

from .models import Organization
from .models import Repository


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
