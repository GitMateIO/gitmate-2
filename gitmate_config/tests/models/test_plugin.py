from inspect import ismodule

from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase
import pytest

from gitmate_config.models import Plugin
from gitmate_config.models import Repository


@pytest.mark.django_db(transaction=False)
class TestPlugin(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            email='john.appleseed@example.com',
            password='top_secret',
            first_name='John',
            last_name='Appleseed'
        )
        self.plugin = Plugin(name='testplugin')
        self.plugin_module = self.plugin.import_module()
        self.plugin.save()
        self.repo = Repository(
            user=self.user, full_name='test', provider='example')
        self.repo.save()

    def test_name(self):
        plugin = Plugin()
        # check default value
        assert plugin.name is None
        # and that field validation fails on empty name
        with pytest.raises(ValidationError):
            plugin.full_clean()
        # trying to save a None name should raise a database error
        with pytest.raises(IntegrityError):
            plugin.save()
        # also empty string must no be allowed
        plugin.name = ''
        # whereby saving empty name strings to database unfortunately works,
        # so never forget to call .full_clean() before custom .save() calls
        with pytest.raises(ValidationError):
            plugin.full_clean()
        plugin.name = 'test'
        plugin.full_clean()

    def test__str__(self):
        plugin = Plugin(name='test')
        assert str(plugin) == 'test'

    def test_import_module(self):
        plugin = Plugin(name='testplugin')
        # import_module should try to import gitmate_{plugin.name}
        module = plugin.import_module()
        assert ismodule(module)
        assert module.__name__ == 'gitmate_testplugin'

    def test_set_settings(self):
        new_settings = {
            'example_bool_setting': False,
            'example_char_setting': 'hello'
        }
        self.plugin.set_settings(self.repo, new_settings)

        modified_settings = self.plugin.get_settings(self.repo)
        assert modified_settings['example_bool_setting'] is False
        assert modified_settings['example_char_setting'] == 'hello'

    def test_get_settings(self):
        settings = self.plugin.get_settings(self.repo)
        assert settings == {'example_bool_setting': True,
                            'example_char_setting': 'example'}
