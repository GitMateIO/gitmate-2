import os
from unittest import TestCase

from django.contrib.auth.models import User
import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_config.views import PluginSettingsView


@pytest.mark.django_db(transaction=False)
class TestSettings(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            first_name="John",
            last_name="Appleseed"
        )

        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN']
        })
        self.auth.save()

        self.repo = Repository(
            user=self.user,
            full_name=os.environ['GITHUB_TEST_REPO'],
            provider=Providers.GITHUB.value)
        self.repo.save()

        self.plugin = Plugin(name="testplugin")
        plugin_module = self.plugin.import_module()
        self.plugin.save()

        self.settings = plugin_module.models.Settings()
        self.settings.repo = self.repo
        self.settings.save()

    def test_get_plugin_settings_no_full_query(self):
        request = self.factory.get('/api/settings')

        request.user = self.user
        response = PluginSettingsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'error': 'Requires valid provider and repo names.'
        })

    def test_get_plugin_settings_no_such_repo(self):
        request = self.factory.get(
            '/api/settings?provider=unknown&repo=unknown')

        request.user = self.user
        response = PluginSettingsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {
            'error': 'No such repository exists.'
        })

    def test_get_plugin_settings(self):
        request = self.factory.get(
            '/api/settings?provider=github&repo=' +
            os.environ['GITHUB_TEST_REPO'])

        request.user = self.user
        response = PluginSettingsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'testplugin': {
                'status': 'inactive',
                'settings': {
                    'example_bool_setting': {
                        'value': True,
                        'description': 'An example Bool setting',
                        'type': 'BooleanField'
                    },
                    'example_char_setting': {
                        'value': 'example',
                        'description': 'An example Char setting',
                        'type': 'CharField'
                    }
                }
            }
        })
