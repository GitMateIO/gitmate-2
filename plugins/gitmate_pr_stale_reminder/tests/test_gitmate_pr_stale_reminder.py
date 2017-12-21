"""
This file contains a sample test case for stale_reminder to be used as
a reference for writing further tests.
"""
from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabIssue import GitLabIssue
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestGitmatePRStaleReminder(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('pr_stale_reminder')
        self.gh_token = GitHubToken(environ['GITHUB_TEST_TOKEN'])
        self.gl_token = GitLabOAuthToken(environ['GITLAB_TEST_TOKEN'])

    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'search_mrs')
    def test_github_pr_sync_stale_label(self, m_search_mrs, m_mr_labels):
        m_mr_labels.return_value = set()
        m_search_mrs.return_value = {
            GitHubMergeRequest(self.gh_token, self.repo.full_name, 7)
        }
        self.simulate_scheduled_responder_call(
            'pr_stale_reminder.add_stale_label_to_merge_requests', self.repo)
        m_mr_labels.assert_called_with({'status/STALE'})

        # testing updated pull requests
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 7},
            'action': 'synchronize'
        }
        m_mr_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_mr_labels.assert_called_with({'bug'})

    @patch.object(GitHubMergeRequest, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'search_mrs')
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    def test_github_pr_comment_stale_label(
            self, m_body, m_search_mrs, m_mr_labels
    ):
        m_mr_labels.return_value = set()
        m_search_mrs.return_value = {
            GitHubMergeRequest(self.gh_token, self.repo.full_name, 7)
        }
        self.simulate_scheduled_responder_call(
            'pr_stale_reminder.add_stale_label_to_merge_requests', self.repo)
        m_mr_labels.assert_called_with({'status/STALE'})

        # testing updated pull requests
        data = {
            'repository': {'full_name': self.repo.full_name,
                           'id': 49558751},
            'issue': {'number': 7, 'pull_request': {}},
            'comment': {'id': 0},
            'action': 'created'
        }
        m_body.return_value = 'This is a mistake.'
        m_mr_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_github_webhook_call('issue_comment', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_mr_labels.assert_called_with({'bug'})


    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'search_mrs')
    def test_gitlab_pr_sync_stale_label(self, m_search_mrs, m_mr_labels):
        m_mr_labels.return_value = set()
        m_search_mrs.return_value = {
            GitLabMergeRequest(self.gl_token, self.gl_repo.full_name, 2)
        }
        self.simulate_scheduled_responder_call(
            'pr_stale_reminder.add_stale_label_to_merge_requests',
            self.gl_repo)
        m_mr_labels.assert_called_with({'status/STALE'})

        # testing updated issues
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': self.gl_repo.full_name},
                'action': 'update',
                'oldrev': 'thisisrequiredforshowingasresyncedpr',
                'iid': 2
            }
        }
        m_mr_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_mr_labels.assert_called_with({'bug'})

    @patch.object(GitLabMergeRequest, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'search_mrs')
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    def test_gitlab_pr_comment_stale_label(
            self, m_body, m_search_mrs, m_mr_labels
    ):
        m_mr_labels.return_value = set()
        m_search_mrs.return_value = {
            GitLabMergeRequest(self.gl_token, self.gl_repo.full_name, 2)
        }
        self.simulate_scheduled_responder_call(
            'pr_stale_reminder.add_stale_label_to_merge_requests',
            self.gl_repo)
        m_mr_labels.assert_called_with({'status/STALE'})

        # testing updated issues
        data = {
            'project': {'path_with_namespace': self.gl_repo.full_name},
            'object_attributes': {
                'action': 'open',
                'id': 2,
                'iid': 0,
                'noteable_type': 'MergeRequest'
            },
            'merge_request': {'iid': 2}
        }
        m_body.return_value = 'I will find you and I will fix you.'
        m_mr_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_gitlab_webhook_call('Note Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_mr_labels.assert_called_with({'bug'})

    def test_does_nothing_on_closed_pull_requests(self):
        self.simulate_scheduled_responder_call(
            'pr_stale_reminder.add_stale_label_to_merge_request', self.repo)

        closed_issue = GitHubMergeRequest(self.gh_token, 'gitmate-test-user/test', 5)
        self.assertEqual(closed_issue.labels, set())
