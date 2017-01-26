from inspect import ismodule

from django.core.management import call_command
import pytest

from gitmate_config.models import Plugin


@pytest.mark.django_db
def test_upmate():
    # before calling upmate no plugins should be registered
    assert not Plugin.objects.all()
    call_command('upmate')
    # after calling the should be only gitmate_testplugin
    plugins = Plugin.objects.all()
    assert len(plugins) == 1
    testplugin = plugins[0]
    assert testplugin.name == 'testplugin'
    testplugin_module = testplugin.import_module()
    assert ismodule(testplugin_module)
    assert testplugin_module.__name__ == 'gitmate_testplugin'
