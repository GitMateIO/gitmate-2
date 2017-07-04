from rest_framework import status
from rest_framework.reverse import reverse

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_config.views import PluginSettingsViewSet


class TestSettings(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')

        settings = self.plugin_module.models.Settings()
        settings.repo = self.repo
        settings.save()

        settings = self.plugin_module.models.Settings()
        settings.repo = self.gl_repo
        settings.save()

        self.plugin_list = PluginSettingsViewSet.as_view(
            actions={'get': 'list'})
        self.plugin_list_url = reverse('api:settings-list')

        self.plugin_retrieve = PluginSettingsViewSet.as_view(
            actions={'get': 'retrieve'})
        self.plugin_retrieve_url = reverse(
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
        repos = [reverse('api:repository-detail',
                         args=(repo.pk,),
                         request=list_plugin_settings_request)
                 for repo in (self.gl_repo, self.repo,)]
        plugin_data = [{
            'name': 'testplugin',
            'title': 'Testing',
            'plugin_category': 'test',
            'description': (
                'A simple plugin used for testing. Smile :)'
            ),
            'active': True,
            'settings': [
                {
                    'name': 'example_char_setting',
                    'value': 'example',
                    'description': 'An example Char setting',
                    'type': 'CharField'
                },
                {
                    'name': 'example_bool_setting',
                    'value': True,
                    'description': 'An example Bool setting',
                    'type': 'BooleanField'
                },
            ]
        }]
        resp_data = [{
            'repository': repo,
            'plugins': plugin_data
        } for repo in repos]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(resp_data[0], response.data)
        self.assertIn(resp_data[1], response.data)

    def test_retrieve_plugin_settings_unauthorized(self):
        retrieve_plugin_settings_request = self.factory.get(
            self.plugin_retrieve_url)
        response = self.plugin_retrieve(
            retrieve_plugin_settings_request,
            pk=self.repo.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_plugin_settings_authorized(self):
        retrieve_plugin_settings_request = self.factory.get(
            self.plugin_retrieve_url)
        retrieve_plugin_settings_request.user = self.user
        response = self.plugin_retrieve(
            retrieve_plugin_settings_request,
            pk=self.repo.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'repository': reverse('api:repository-detail',
                                  args=(self.repo.pk,),
                                  request=retrieve_plugin_settings_request),
            'plugins': [
                {
                    'name': 'testplugin',
                    'title': 'Testing',
                    'plugin_category': 'test',
                    'description': (
                        'A simple plugin used for testing. Smile :)'
                    ),
                    'active': True,
                    'settings': [
                        {
                            'name': 'example_char_setting',
                            'value': 'example',
                            'description': 'An example Char setting',
                            'type': 'CharField'
                        },
                        {
                            'name': 'example_bool_setting',
                            'value': True,
                            'description': 'An example Bool setting',
                            'type': 'BooleanField'
                        },
                    ]
                }
            ]
        })

    def test_update_plugin_settings_authorized(self):
        settings = [{
            'name': 'testplugin',
            'active': True,
            'settings': {
                'example_bool_setting': False,
                'example_char_setting': 'hello'
            }
        }]
        update_plugin_settings_request = self.factory.patch(
            self.plugin_retrieve_url,
            settings,
            HTTP_HOST='testing.com', format='json')
        update_plugin_settings_request.user = self.user
        response = self.plugin_update(
            update_plugin_settings_request,
            pk=self.repo.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
