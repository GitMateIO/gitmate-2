from unittest.mock import patch
from unittest.mock import PropertyMock

from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.Interfaces.Comment import CommentType
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Utils import CachedDataMixin

from gitmate_config.models import Repository
from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_hooks.responders import remove_non_existent_repos
from gitmate_hooks.utils import run_plugin_for_all_repos
from gitmate_hooks.utils import ResponderRegistrar


class TestResponderRegistrar(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('testplugin')

        @ResponderRegistrar.responder(self.plugin.name,
                                      MergeRequestActions.OPENED)
        def test_responder(obj, example_bool_setting: bool = True):
            return example_bool_setting

        @ResponderRegistrar.scheduled_responder(
            self.plugin.name, 100.00, is_active=True)
        def scheduled_responder_function(obj, example_bool_setting: bool=True):
            return example_bool_setting

    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    def test_blocked_comment_response(self, m_body):

        @ResponderRegistrar.responder(self.plugin.name,
                                      MergeRequestActions.COMMENTED)
        def test_blocked_responder(mr, comment, *args, **kwargs):
            # this should never run
            return comment.body  # pragma: no cover

        mr = GitHubMergeRequest(None, 'test/1', 0)
        comment = GitHubComment(None, 'test/1', CommentType.MERGE_REQUEST, 0)
        m_body.return_value = ('Hello\n'
                               '(Powered by [GitMate.io](https://gitmate.io))')

        # ensures that the event was blocked, if it weren't it will return the
        # comment body.
        self.assertEqual(
            [result.get() for result in ResponderRegistrar.respond(
                MergeRequestActions.COMMENTED, mr, comment, repo=self.repo)],
            []
        )

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

    @patch.object(CachedDataMixin, 'refresh')
    def test_remove_non_existant_repos(self, m_refresh):
        self.assertEqual(len(Repository.objects.all()), 3)
        m_refresh.side_effect = RuntimeError('404 not found', 404)
        remove_non_existent_repos()
        # Only gh_app_repo remains after deletion
        self.assertEqual(len(Repository.objects.all()), 1)
