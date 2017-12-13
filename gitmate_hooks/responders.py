"""
This module contains basic functions to create, update and delete entries from
a database. The current scope of this module does not require testing as it is
only basic operations on Django models.
"""
from typing import List

from IGitt.Interfaces.Actions import InstallationActions
from IGitt.Interfaces.Repository import Repository as IGittRepository
from IGitt.Interfaces.Installation import Installation as IGittInstallation

from gitmate_config.models import Installation
from gitmate_config.models import Repository
from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.responder(
    'hooks',
    InstallationActions.CREATED,
    InstallationActions.REPOSITORIES_ADDED
)
def update_installed_repositories(
        installation: IGittInstallation, repos: List[IGittRepository]
):
    """
    Creates and updates an installation object in the database.
    """
    db_installation, _ = Installation.objects.get_or_create(
        provider=installation.hoster, identifier=installation.identifier)
    for repo in repos:
        Repository.objects.get_or_create(
            provider=repo.hoster, identifier=repo.identifier,
            full_name=repo.full_name, installation=db_installation,
            active=True)


@ResponderRegistrar.responder('hooks', InstallationActions.DELETED)
def delete_installation(installation: IGittInstallation):
    """
    Deletes an installation object from the database.
    """
    Installation.from_igitt_installation(installation).delete()


@ResponderRegistrar.responder(
    'hooks', InstallationActions.REPOSITORIES_REMOVED)
def remove_installed_repositories(
        _: IGittInstallation, repos: [IGittRepository]
):
    """
    Removes repositories from an existing installation.
    """
    for repo in repos:
        db_repo = Repository.from_igitt_repo(repo)
        db_repo.installation = None
        db_repo.save()
