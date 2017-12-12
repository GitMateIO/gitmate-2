from unittest.mock import patch

from IGitt.Interfaces.Actions import MergeRequestActions

from gitmate_config.models import Plugin
from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_hooks.utils import ResponderRegistrar, run_plugin_for_all_repos
from gitmate.utils import ScheduledTasks


class TestResponderRegistrar(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')

        @ResponderRegistrar.responder(self.plugin.name,
                                      MergeRequestActions.OPENED)
        def test_responder(obj, example_bool_setting: bool = True):
            return example_bool_setting

        @ResponderRegistrar.scheduled_responder(self.plugin.name,
                100.00,
                is_active=True)
        def scheduled_responder_function(obj, example_bool_setting: bool=True):
            return example_bool_setting

    def test_active_plugin(self):
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.OPENED, 'example', repo=self.repo)],
            [True]
        )
        self.repo.set_plugin_settings([{
            'name': 'testplugin',
            'settings': {
                'example_bool_setting': False
            }
        }])
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.OPENED, 'example', repo=self.repo)],
            [False]
        )

    def test_active_plugin_scheduled_responder(self):
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                'testplugin.scheduled_responder_function',
                self.repo.igitt_repo,
                repo=self.repo)],
            [True, True]
        )

    @patch.object(ResponderRegistrar, 'respond', return_value=None)
    def test_run_plugin_for_all_repos(self, m_respond):
        run_plugin_for_all_repos(self.plugin,
                                 'testplugin.scheduled_responder_function',
                                 True)
        self.assertEqual(m_respond.call_count, 2)

    def test_inactive_plugin(self):
        # Clearing all plugins!
        self.repo.plugins.all().delete()

        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.OPENED, 'example', repo=self.repo)],
            []
        )
