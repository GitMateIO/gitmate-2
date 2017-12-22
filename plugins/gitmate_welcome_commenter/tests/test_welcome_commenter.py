from os import environ
from unittest.mock import patch

from django.core.signing import TimestampSigner
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestWelcomeCommenter(GitmateTestCase):

    def setUp(self):
        self.signer = TimestampSigner()
        super().setUpWithPlugin('welcome_commenter')

    @patch.object(GitHubMergeRequest, 'add_comment')
    def test_github(self, mock_add_comment):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 7},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sign = self.signer.sign('')
        msg = ('\n\n(Powered by [GitMate.io](https://gitmate.io))\n\n'
               '<!-- Timestamp signature `{}` -->'.format(sign))
        mock_add_comment.assert_called_once_with(msg)

    @patch.object(GitLabMergeRequest, 'add_comment')
    def test_gitlab(self, mock_add_comment):
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 2
            }
        }
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sign = self.signer.sign('')
        msg = ('\n\n(Powered by [GitMate.io](https://gitmate.io))\n\n'
               '<!-- Timestamp signature `{}` -->'.format(sign))
        mock_add_comment.assert_called_once_with(msg)
