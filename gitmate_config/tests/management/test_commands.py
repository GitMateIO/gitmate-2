from inspect import ismodule
from shutil import rmtree

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_config.models import User


@pytest.mark.django_db
def test_upmate():
    # before calling upmate no plugins should be registered
    assert not Plugin.objects.all()
    call_command('upmate')
    # after calling the should be only gitmate_testplugin
    plugins = Plugin.objects.all()
    assert len(plugins) == len(settings.GITMATE_PLUGINS)
    testplugin = plugins[0]
    assert testplugin.name == 'testplugin'
    testplugin_module = testplugin.import_module()
    assert ismodule(testplugin_module)
    assert testplugin_module.__name__ == 'gitmate_testplugin'
    user = User.objects.create_user(
        username='john',
        email='john.appleseed@example.com',
        password='top_secret',
        first_name='John',
        last_name='Appleseed')
    repo = Repository(
        user=user, full_name='test', provider='example')
    repo.save()
    call_command('upmate')
    repo.plugins.add(testplugin)
    assert repo.get_plugin_settings() == {
        'example_bool_setting': True,
        'example_char_setting': 'example'
    }


def test_startplugin():
    # pre existent plugin match
    with pytest.raises(CommandError):
        call_command('startplugin', 'testplugin')

    call_command('startplugin', 'star_wars')
    rmtree('gitmate_star_wars')
