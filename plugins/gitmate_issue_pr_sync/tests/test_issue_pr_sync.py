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

    @patch.object(GitHubMergeRequest, 'assign', return_value=None)
    @patch.object(GitHubMergeRequest, 'unassign', return_value=None)
    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    def test_github(self, m_labels, m_unassign, m_assign):

        # setting the labels
        GitHubIssue.labels = {'a', 'b'}
        GitHubIssue.assignees = ('gitmate-test-user', )
        GitHubMergeRequest.assignees = tuple()
        m_labels.return_value = set()

        # testing updated pull requests
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 110},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'a', 'b'})
        m_assign.assert_called_with('gitmate-test-user')

        # testing updated issue
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'issue': {'number': 104},
            'action': 'updated'
        }
        GitHubIssue.labels = {'a'}
        GitHubIssue.assignees = ('sils', )
        GitHubMergeRequest.assignees = ('gitmate-test-user', )

        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'a'})
        m_unassign.assert_called_with('gitmate-test-user')
        m_assign.assert_called_with('sils')

    @patch.object(GitHubMergeRequest, 'assign', return_value=None)
    @patch.object(GitHubMergeRequest, 'unassign', return_value=None)
    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    def test_no_assignment(self, m_labels, m_unassign, m_assign):
        settings = [
            {
                'name': 'issue_pr_sync',
                'settings': {
                    'sync_assignees': False,
                }
            }
        ]
        self.repo.set_plugin_settings(settings)

        # setting the labels
        GitHubIssue.labels = {'a', 'b'}
        GitHubIssue.assignees = ('gitmate-test-user', )
        GitHubMergeRequest.assignees = tuple()
        m_labels.return_value = set()

        # testing updated pull requests
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 110},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'a', 'b'})
        m_assign.assert_not_called()

        # testing updated issue
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'issue': {'number': 104},
            'action': 'updated'
        }
        GitHubIssue.labels = {'a'}
        GitHubIssue.assignees = ('sils', )
        GitHubMergeRequest.assignees = ('gitmate-test-user', )

        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'a'})
        m_unassign.assert_not_called()
        m_assign.assert_not_called()

    @patch.object(GitLabMergeRequest, 'assign', return_value=None)
    @patch.object(GitLabMergeRequest, 'unassign', return_value=None)
    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    def test_gitlab(self, m_labels, m_unassign, m_assign):

        # setting the labels
        GitLabIssue.labels = {'a', 'b'}
        GitLabIssue.assignees = ('gitmate-test-user', )
        GitLabMergeRequest.assignees = tuple()
        m_labels.return_value = set()

        # testing updated pull requests
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

        m_labels.assert_called()
        m_labels.assert_called_with({'a', 'b'})
        m_assign.assert_called_with('gitmate-test-user')

        # testing updated issue
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'update',
                'iid': 21
            }
        }
        GitLabIssue.labels = {'a'}
        GitLabIssue.assignees = ('sils', )
        GitLabMergeRequest.assignees = ('gitmate-test-user', )

        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        # the label 'b' remains due to other issues
        m_labels.assert_called_with({'a', 'b'})
        # no unassign calls because other issues still have 'gitmate-test-user'
        m_unassign.assert_not_called()
        # new assignee 'sils' would be added though
        m_assign.assert_called_with('sils')
