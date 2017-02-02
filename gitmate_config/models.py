from importlib import import_module

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import models


class Plugin(models.Model):
    name = models.CharField(
        # default None ensures that trying to save a Plugin instance
        # with uninitialized name will be forbidden on database level
        default=None, max_length=50)

    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def import_module(self):
        return import_module('gitmate_' + self.name)


class Repository(models.Model):

    # The user who owns the repository
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The provider for the hosted repository
    provider = models.CharField(default=None, max_length=32)

    # The full name of the repository along with username
    full_name = models.CharField(default=None, max_length=255)

    active = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    class Meta:
        unique_together = ('provider', 'full_name')
