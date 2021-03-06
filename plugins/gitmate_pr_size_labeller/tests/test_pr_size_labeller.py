from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest


class TestPRSizeLabeller(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('pr_size_labeller')
        self.github_data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 7},
            'action': 'synchronize'
        }
        self.gitlab_data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'update',
                'oldrev': 'gitmatesavestheday',
                'iid': 2
            }
        }
        self.test_labels = {
            'size/XS': (10, 10),
            'size/S': (100, 100),
            'size/M': (200, 200),
            'size/L': (400, 400),
            'size/XL': (700, 700),
            'size/XXL': (1000, 1000),
        }

    @patch.object(GitHubMergeRequest, 'diffstat', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    def test_github(self, m_labels, m_diffstat):
        for label, diffstat in self.test_labels.items():
            m_diffstat.return_value = diffstat
            response = self.simulate_github_webhook_call('pull_request',
                                                         self.github_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check for label getter call
            m_labels.assert_called()

            # Check for label setter call
            m_labels.assert_called_with({label})

    @patch.object(GitLabMergeRequest, 'diffstat', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    def test_gitlab(self, m_labels, m_diffstat):
        for label, diffstat in self.test_labels.items():
            m_diffstat.return_value = diffstat
            response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                         self.gitlab_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Check for label getter call
            m_labels.assert_called()

            # Check for label setter call
            m_labels.assert_called_with({label})
