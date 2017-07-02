"""
This module contains the models related to igitt_django app.
"""
from django.contrib.postgres import fields as psql_fields
from django.db import models


class IGittBase(models.Model):
    """
    An abstract base model for IGitt django models.
    """
    extra_data = psql_fields.JSONField()

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
