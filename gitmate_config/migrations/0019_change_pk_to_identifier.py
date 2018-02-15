# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-30 07:41
from __future__ import unicode_literals
import logging

from django.db import migrations

from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab.GitLabRepository import GitLabRepository
from gitmate_config.enums import Providers


def get_token(repo):
    if repo.installation is not None:
        return repo.installation.token

    raw_token = repo.user.social_auth.get(
        provider=repo.provider).access_token

    return Providers(repo.provider).get_token(
        raw_token,
        private_token='private_token' in repo.user.social_auth.get(
            provider=repo.provider).extra_data
    )


def get_identifier(repo):
    if repo.provider == Providers.GITHUB.value:
        return GitHubRepository(get_token(repo), repo.full_name).identifier
    elif repo.provider == Providers.GITLAB.value:
        return GitLabRepository(get_token(repo), repo.full_name).identifier


def save_identifier(apps, schema_editor):
    Repository = apps.get_model('gitmate_config', 'Repository')
    for repo in Repository.objects.filter(identifier__isnull=True):
        try:
            repo.identifier = get_identifier(repo)
            repo.save()
        except Exception as ex:
            # If a user token was revoked, or any other error occurs, it should
            # be skipped and migration continues.
            logging.exception(
                f'ERROR: Fetching identifier for {repo} failed.\n'
                f'Exception:   {repr(ex)}\n')



class Migration(migrations.Migration):

    dependencies = [
        ('gitmate_config', '0018_auto_20180130_0738'),
    ]

    operations = [
        migrations.RunPython(save_identifier)
    ]
