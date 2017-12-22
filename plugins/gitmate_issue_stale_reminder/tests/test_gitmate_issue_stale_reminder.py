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


class TestGitmateIssueStaleReminder(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('issue_stale_reminder')
        self.gh_token = GitHubToken(environ['GITHUB_TEST_TOKEN'])
        self.gl_token = GitLabOAuthToken(environ['GITLAB_TEST_TOKEN'])

    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'search_issues')
    def test_github_issue_reopened_stale_label(
        self, m_search_issues, m_issue_labels
    ):
        m_issue_labels.return_value = set()
        m_search_issues.return_value = {
            GitHubIssue(self.gh_token, self.repo.full_name, 104)
        }
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.repo)
        m_issue_labels.assert_called_with({'status/STALE'})

        # testing updated issue
        data = {
            'repository': {'full_name': self.repo.full_name, 'id': 49558751},
            'issue': {'number': 104},
            'action': 'reopened'
        }
        m_issue_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_issue_labels.assert_called_with({'bug'})

    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'search_issues')
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    def test_github_issue_comment_stale_label(
        self, m_body, m_search_issues, m_issue_labels
    ):
        m_issue_labels.return_value = set()
        m_search_issues.return_value = {
            GitHubIssue(self.gh_token, self.repo.full_name, 104)
        }
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.repo)
        m_issue_labels.assert_called_with({'status/STALE'})

        # testing added comment to issue
        data = {
            'repository': {'full_name': self.repo.full_name, 'id': 49558751},
            'issue': {'number': 7},
            'comment': {'id': 0},
            'action': 'created'
        }
        m_body.return_value = 'Luke is back!'
        m_issue_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_github_webhook_call('issue_comment', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_issue_labels.assert_called_with({'bug'})

    @patch.object(
        GitHubMergeRequest, 'mentioned_issues', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'search_issues')
    def test_github_merge_request_mention_stale_label(
        self, m_search_issues, m_issue_labels, m_mentioned_issues
    ):
        m_issue_labels.return_value = set()
        m_search_issues.return_value = {
            GitHubIssue(self.gh_token, self.repo.full_name, 104)
        }
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.repo)
        m_issue_labels.assert_called_with({'status/STALE'})

        # testing issue mentioned in a PR
        data = {
            'repository': {'full_name': self.repo.full_name, 'id': 49558751},
            'pull_request': {'number': 7},
            'action': 'opened'
        }

        m_issue_labels.return_value = {'bug', 'status/STALE'}

        m_mentioned_issues.return_value = {
            GitHubIssue(self.gh_token, self.repo.full_name, 104)}
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_issue_labels.assert_called_with({'bug'})

    @patch.object(GitLabIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'search_issues')
    def test_gitlab_issue_reopened_stale_label(
        self, m_search_issues, m_issue_labels
    ):
        m_issue_labels.return_value = set()
        m_search_issues.return_value = {
            GitLabIssue(self.gl_token, self.gl_repo.full_name, 21)
        }
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.gl_repo)
        m_issue_labels.assert_called_with({'status/STALE'})

        # testing updated issues
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'reopen',
                'iid': 21
            }
        }
        m_issue_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_issue_labels.assert_called_with({'bug'})

    @patch.object(GitLabIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'search_issues')
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    def test_gitlab_issue_commented_stale_label(
        self, m_body, m_search_issues, m_issue_labels
    ):
        m_issue_labels.return_value = set()
        m_search_issues.return_value = {
            GitLabIssue(self.gl_token, self.gl_repo.full_name, 21)
        }
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.gl_repo)
        m_issue_labels.assert_called_with({'status/STALE'})

        # testing updated issues
        data = {
            'project': {'path_with_namespace': self.gl_repo.full_name},
            'object_attributes': {
                'action': 'open',
                'id': 25,
                'iid': 0,
                'noteable_type': 'Issue'
            },
            'issue': {'iid': 21}
        }
        m_body.return_value = 'Hello world, dudes!'
        m_issue_labels.return_value = {'bug', 'status/STALE'}
        response = self.simulate_gitlab_webhook_call('Note Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_issue_labels.assert_called_with({'bug'})

    @patch.object(
        GitLabMergeRequest, 'mentioned_issues', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'search_issues')
    def test_gitlab_merge_request_mention_stale_label(
        self, m_search_issues, m_issue_labels, m_mentioned_issues
    ):
        m_issue_labels.return_value = set()
        m_search_issues.return_value = {
            GitLabIssue(self.gl_token, self.gl_repo.full_name, 21)
        }
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.gl_repo)
        m_issue_labels.assert_called_with({'status/STALE'})

        # testing issue mentioned in a PR
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 8
            }
        }
        m_issue_labels.return_value = {'bug', 'status/STALE'}

        m_mentioned_issues.return_value = {
            GitLabIssue(self.gl_token, self.gl_repo.full_name, 21)}
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # only the 'bug' label remains after removing 'status/STALE'
        m_issue_labels.assert_called_with({'bug'})

    def test_does_nothing_on_closed_issues(self):
        self.simulate_scheduled_responder_call(
            'issue_stale_reminder.add_stale_label_to_issues', self.repo)

        closed_issue = GitHubIssue(self.gh_token, 'gitmate-test-user/test', 87)
        self.assertEqual(closed_issue.labels, set())
