from os import environ
from unittest.mock import patch

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestWelcomeCommenter(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('welcome_commenter')

    @patch('IGitt.GitHub.GitHubIssue.GitHubIssue.add_comment', autospec=True)
    def test_github(self, mock_add_comment):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 7},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        mock_add_comment.assert_called_once()
