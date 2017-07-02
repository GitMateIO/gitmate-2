"""
This module contains the models related to igitt_django app.
"""
from django.contrib.postgres import fields as psql_fields
from django.db import models

from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.Interfaces.Repository import Repository

from igitt_django import Providers


class IGittBase(models.Model):
    """
    An abstract base model for IGitt django models.
    """
    extra_data = psql_fields.JSONField(default={})

    def __str__(self):
        raise NotImplementedError

    @classmethod
    def from_igitt_instance(cls, obj):
        """
        A base method that creates a model from an igitt object.
        """
        raise NotImplementedError

    def to_igitt_instance(self, raw_token: str):
        """
        Returns the related igitt instance.
        """
        raise NotImplementedError

    class Meta:
        abstract = True
        app_label = 'igitt_django'
        required_db_vendor = 'postgres'


class AbstractRepository(IGittBase):
    """
    An abstract model representing IGitt compatible repository object.
    """
    provider = models.CharField(default=None, max_length=64)
    full_name = models.CharField(default=None, max_length=256)

    def __str__(self):
        return '{}/{}'.format(self.provider, self.full_name)

    @classmethod
    def from_igitt_instance(cls, obj: Repository):
        """
        Returns a Repository model instance from IGitt Repository object.
        """
        return cls(
            provider=obj.hoster, full_name=obj.full_name, extra_data=obj.data)

    def to_igitt_instance(self, raw_token: str) -> Repository:
        """
        Returns the related Repository object.
        """
        if self.provider == Providers.GITHUB.value:
            token = Providers.GITHUB.get_token(raw_token)
            return GitHubRepository(token, self.full_name)
        elif self.provider == Providers.GITLAB.value:
            token = Providers.GITLAB.get_token(raw_token)
            return GitLabRepository(token, self.full_name)

        # other providers aren't implemented yet.
        raise NotImplementedError

    class Meta:
        abstract = True


class IGittRepository(AbstractRepository):
    """
    A complete model representing IGitt compatible repository object.
    """
    class Meta:
        unique_together = ('provider', 'full_name')
        verbose_name_plural = 'igitt_repositories'
