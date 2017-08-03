from unittest.mock import patch

from IGitt.Interfaces.Actions import MergeRequestActions

from gitmate_config.models import Plugin
from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_hooks import ResponderRegistrar, run_plugin_for_all_repos
from gitmate.utils import ScheduledTasks


class TestResponderRegistrar(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')

        @ResponderRegistrar.responder(self.plugin,
                                      MergeRequestActions.OPENED)
        def test_responder(obj, test_var: bool = True):
            return test_var

        @ResponderRegistrar.scheduled_responder(self.plugin,
                100.00,
                is_active=True)
        def scheduled_responder_function(obj, example_bool_setting: bool=True):
            return example_bool_setting

    def test_active_plugin(self):
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.OPENED, self.repo, 'example',
                options={'test_var': True})],
            [True]
        )
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.OPENED, self.repo, 'example',
                options={'test_var': False})],
            [False]
        )

    def test_active_plugin_scheduled_responder(self):
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                'testplugin.scheduled_responder_function', self.repo,
                self.repo.igitt_repo,
                options={'example_bool_setting': True})],
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
                MergeRequestActions.OPENED, self.repo, 'example',
                options={'test_var': True})],
            []
        )
