from os import environ
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import PropertyMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest


class TestAutoLabelPendingOrWip(GitmateTestCase):

    def setUp(self):
        self.setUpWithPlugin('auto_label_pending_or_wip')
        self.github_data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 7},
            'action': 'edited'
        }
        self.gitlab_data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'update',
                'iid': 2
            }
        }

    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    def test_github_change_label_to_process_pending(self, mocked_labels):
        mocked_labels.return_value.add = MagicMock()
        response = self.simulate_github_webhook_call(
            'pull_request', self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mocked_labels().add.assert_called_with('process/pending_review')

    @patch.object(GitHubMergeRequest, 'title',
                  new_callable=PropertyMock,
                  return_value='WIP: Fühl mich betrunken')
    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    def test_github_change_label_to_process_wip(self, mocked_labels, *args):
        mocked_labels.return_value.add = MagicMock()
        response = self.simulate_github_webhook_call(
            'pull_request', self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mocked_labels().add.assert_called_with('process/WIP')

    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    def test_gitlab_change_label_to_process_pending(self, mocked_labels):
        mocked_labels.return_value.add = MagicMock()
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', self.gitlab_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mocked_labels().add.assert_called_with('process/pending_review')

    @patch.object(GitLabMergeRequest, 'title',
                  new_callable=PropertyMock,
                  return_value='WIP: Fühl mich betrunken')
    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    def test_gitlab_change_label_to_process_wip(self, mocked_labels, *args):
        mocked_labels.return_value.add = MagicMock()
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', self.gitlab_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mocked_labels().add.assert_called_with('process/WIP')
