from importlib import import_module

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
