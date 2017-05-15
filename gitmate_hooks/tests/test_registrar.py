from django.test import override_settings
from IGitt.Interfaces.Actions import MergeRequestActions

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_hooks import ResponderRegistrar


@override_settings(CELERY_ALWAYS_EAGER=True)
class TestResponderRegistrar(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')

        @ResponderRegistrar.responder(self.plugin,
                                      MergeRequestActions.OPENED)
        def test_responder(obj, test_var: bool = True):
            return test_var

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

    def test_inactive_plugin(self):
        # Clearing all plugins!
        self.repo.plugins.all().delete()

        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.OPENED, self.repo, 'example',
                options={'test_var': True})],
            []
        )
