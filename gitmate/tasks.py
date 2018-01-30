from django.conf import settings

from gitmate.celery import app as celery
from gitmate_config.models import Installation
from gitmate_config.models import Repository


@celery.task
def populate_github_repositories(db_user, igitt_user):
    for inst in igitt_user.get_installations(settings.GITHUB_JWT):
        # create this installation object, if it wasn't created before
        db_inst, created = Installation.objects.get_or_create(
            provider=inst.hoster, identifier=inst.identifier)
        db_inst.admins.add(db_user)
        if not created:
            db_inst.save()
            return

        # create repos for this installation, if they weren't populated before
        for repo in inst.repositories:
            Repository.objects.get_or_create(
                identifier=repo.identifier,
                provider=repo.hoster,
                installation=db_inst,
                defaults={
                    'installation': db_inst,
                    'active': True,
                    'identifier': repo.identifier,
                    'full_name': repo.full_name
                })
