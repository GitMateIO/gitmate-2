from shutil import rmtree

from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from gitmate_config.tests.test_base import GitmateTestCase


class TestCommands(GitmateTestCase):
    def test_startplugin(self):
        # pre existent plugin match
        with pytest.raises(CommandError):
            call_command('startplugin', 'testplugin')

        call_command('startplugin', 'star_wars')
        rmtree('plugins/gitmate_star_wars')
