from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock
from unittest.mock import MagicMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubCommit import GitHubCommit


class TestAck(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('ack')

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, '__init__', return_value=None)
    @patch.object(GitHubComment, '__init__', return_value=None)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'ack', new_callable=MagicMock)
    @patch.object(GitHubCommit, '__init__', return_value=None)
    def test_github_ack(self,
                        m_commit,
                        m_ack,
                        m_sha,
                        m_body,
                        m_cmt,
                        m_pr,
                        m_commits):

        m_sha.return_value = '26b5d363f0845873c46cbe3eefff0f1263c47606'
        m_body.return_value = 'ack 26b5d36'
        m_commits.return_value = tuple([GitHubCommit()])

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'issue': {'number': 10},
            'comment': {'id': 0},
            'action': 'created'
            }

        response = self.simulate_github_webhook_call('issue_comment', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_ack.assert_called()

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, '__init__', return_value=None)
    @patch.object(GitHubComment, '__init__', return_value=None)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'unack', new_callable=MagicMock)
    @patch.object(GitHubCommit, '__init__', return_value=None)
    def test_github_unack(self,
                          m_commit,
                          m_unack,
                          m_sha,
                          m_body,
                          m_cmt,
                          m_pr,
                          m_commits):

        m_sha.return_value = '26b5d363f0845873c46cbe3eefff0f1263c47606'
        m_body.return_value = 'unack 26b5d36'
        m_commits.return_value = tuple([GitHubCommit()])

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'issue': {'number': 0},
            'comment': {'id': 0},
            'action': 'created'
            }

        response = self.simulate_github_webhook_call('issue_comment', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_unack.assert_called()

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, '__init__', return_value=None)
    @patch.object(GitHubCommit, 'pending', new_callable=MagicMock)
    @patch.object(GitHubCommit, '__init__', return_value=None)
    def test_github_pending_pr_open_event(self,
                                          mock_commit,
                                          mock_pending,
                                          mock_pr,
                                          mock_commits):
        mock_commits.return_value = tuple([GitHubCommit()])

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 0},
            'action': 'opened'
            }

        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_pending.assert_called()
