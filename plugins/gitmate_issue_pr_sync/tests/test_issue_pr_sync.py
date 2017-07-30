from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest


class TestIssuePRSync(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('issue_pr_sync')

    @patch.object(GitHubIssue, 'assignees', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'assign', return_value=None)
    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    def test_github(
            self, m_labels, m_assign, m_issue_labels, m_issue_assignees
    ):
        # setting the labels for issues
        m_issue_labels.return_value = {'a', 'b'}
        # setting the assignees for issues
        m_issue_assignees.return_value = {'gitmate-test-user'}

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 110},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # gets the set of labels and adds new ones onto it
        m_labels.assert_called()
        m_labels.assert_called_with({'a', 'b'})

        m_assign.assert_called_with('gitmate-test-user')

    @patch.object(GitLabIssue, 'assignees', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'assign', return_value=None)
    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    def test_gitlab(
            self, m_labels, m_assign, m_issue_labels, m_issue_assignees
    ):
        # setting the labels for issues
        m_issue_labels.return_value = {'a', 'b'}
        # setting the assignees for issues
        m_issue_assignees.return_value = {'gitmate-test-user'}

        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 25
            }
        }
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # gets the set of labels and adds new ones onto it
        m_labels.assert_called()
        m_labels.assert_called_with({'a', 'b'})

        m_assign.assert_called_with('gitmate-test-user')
