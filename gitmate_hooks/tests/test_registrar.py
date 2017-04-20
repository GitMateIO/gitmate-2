from unittest import TestCase

from IGitt.Interfaces.Actions import MergeRequestActions
import pytest

from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_config.models import User
from gitmate_hooks import ResponderRegistrar

MergeRequestActions.OPENED


@pytest.mark.django_db(transaction=False)
class TestResponderRegistrar(TestCase):

    def setUp(self):
        # Name is important, it'll import gitmate_testplugin
        self.SomePlugin = Plugin.objects.create(name='testplugin')
        self.SomePlugin.save()

        self.SomeUser = User()
        self.SomeUser.save()

        self.SomeRepo = Repository.objects.create(
            user=self.SomeUser,
            full_name='some/repo',
            provider='github',
        )
        self.SomeRepo.save()

        @ResponderRegistrar.responder(self.SomePlugin,
                                      MergeRequestActions.OPENED)
        def test_responder(obj, test_var: bool = True):
            return test_var

    def test_active_plugin(self):
        self.SomeRepo.plugins.add(self.SomePlugin)
        self.SomeRepo.save()

        self.assertEqual(
            ResponderRegistrar.respond(
                MergeRequestActions.OPENED, self.SomeRepo, 'example',
                options={'test_var': True}),
            [True]
        )
        self.assertEqual(
            ResponderRegistrar.respond(
                MergeRequestActions.OPENED, self.SomeRepo, 'example',
                options={'test_var': False}),
            [False]
        )

    def test_inactive_plugin(self):
        self.assertEqual(
            ResponderRegistrar.respond(
                MergeRequestActions.OPENED, self.SomeRepo, 'example',
                options={'test_var': True}
            ),
            []
        )
