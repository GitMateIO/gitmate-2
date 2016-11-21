from importlib import import_module

from django.db import models


class Plugin(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField()

    def import_module(self):
        return import_module('gitmate_' + self.name)
