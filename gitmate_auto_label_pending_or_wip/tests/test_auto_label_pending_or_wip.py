from os import environ
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import PropertyMock

from IGitt.GitHub.GitHubIssue import GitHubIssue
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestAutoLabelPendingOrWip(GitmateTestCase):

    def setUp(self):
        self.setUpWithPlugin('auto_label_pending_or_wip')
        self.github_data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 7},
            'action': 'synchronize'
        }

    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    def test_github_change_label_to_process_pending(self, mocked_labels):
        mocked_labels.return_value.add = MagicMock()
        response = self.simulate_github_webhook_call(
            'pull_request', self.github_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        mocked_labels().add.assert_called_with('process/pending_review')

    @patch.object(GitHubIssue, 'title',
                  new_callable=PropertyMock,
                  return_value='WIP: Fühl mich betrunken')
    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    def test_github_change_label_to_process_wip(self, mocked_labels, *args):
        mocked_labels.return_value.add = MagicMock()
        response = self.simulate_github_webhook_call(
            'pull_request', self.github_data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        mocked_labels().add.assert_called_with('process/WIP')
