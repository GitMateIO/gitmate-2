import os
from unittest import TestCase

from django.contrib.auth.models import User
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_config.views import PluginSettingsViewSet


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

        self.plugin_list = PluginSettingsViewSet.as_view(
            actions={'get': 'list'})
        self.plugin_list_url = reverse('api:settings-list')

        self.plugin_retrieve = PluginSettingsViewSet.as_view(
            actions={'get': 'retrieve'})
        self.plugin_retrive_url = reverse(
            'api:settings-detail',
            args=(self.repo.pk,))

        self.plugin_update = PluginSettingsViewSet.as_view(
            actions={'put': 'update', 'patch': 'partial_update'})

    def test_list_plugin_settings_unauthorized(self):
        list_plugin_settings_request = self.factory.get(self.plugin_list_url)
        response = self.plugin_list(list_plugin_settings_request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_plugin_settings_authorized(self):
        list_plugin_settings_request = self.factory.get(self.plugin_list_url)
        list_plugin_settings_request.user = self.user
        response = self.plugin_list(list_plugin_settings_request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [{
            'repository': reverse('api:repository-detail',
                                  args=(self.repo.pk,)),
            'plugins': {
                'testplugin': {
                    'active': False,
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
            }
        }])

    def test_retrive_plugin_settings_unauthorized(self):
        retrieve_plugin_settings_request = self.factory.get(
            self.plugin_list_url)
        response = self.plugin_retrieve(
            retrieve_plugin_settings_request,
            pk=self.repo.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrive_plugin_settings_authorized(self):
        retrieve_plugin_settings_request = self.factory.get(
            self.plugin_list_url)
        retrieve_plugin_settings_request.user = self.user
        response = self.plugin_retrieve(
            retrieve_plugin_settings_request,
            pk=self.repo.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'repository': reverse('api:repository-detail',
                                  args=(self.repo.pk,)),
            'plugins': {
                'testplugin': {
                    'active': False,
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
            }
        })

    def test_update_plugin_settings_authorized(self):
        settings = [{
            'name': 'testplugin',
            'active': True,
            'settings': {
                'example_bool_setting': False,
                'example_char_setting': "hello"
            }
        }]
        update_plugin_settings_request = self.factory.patch(
            self.plugin_retrive_url,
            settings,
            HTTP_HOST='testing.com', format='json')
        update_plugin_settings_request.user = self.user
        response = self.plugin_update(
            update_plugin_settings_request,
            pk=self.repo.pk)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
