"""
This file contains a sample test case for rebaser to be used as
a reference for writing further tests.
"""
from collections import namedtuple
from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock
import subprocess

from rest_framework import status
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_config.tests.test_base import StreamMock


PopenResult = namedtuple('ret', 'stdout wait')


def fake_popen_success(cmd, **kwargs):
    if 'run.py' in cmd:
        return PopenResult(StreamMock('{"status": "success"}'), lambda: None)


def fake_popen_failure(cmd, **kwargs):
    if 'run.py' in cmd:
        return PopenResult(
            StreamMock(
                '{"status": "error", "error": "Command \'[\'git\', \'rebase\''
                ', \'master\']\' returned non-zero exit status 128."}'),
            lambda: None)


class TestGitmateRebaser(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('rebaser')
        self.github_data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'issue': {
                'number': 108,
                'pull_request': {},
            },
            'comment': {'id': 322317220},
            'action': 'created'
        }
        self.gitlab_data = {
            'project': {
                'path_with_namespace': environ['GITLAB_TEST_REPO'],
            },
            'object_attributes': {
                'id': 37544128,
                'noteable_type': 'MergeRequest'
            },
            'merge_request': {'iid': 20}
        }
        self.old_popen = subprocess.Popen

    def tearDown(self):
        subprocess.Popen = self.old_popen

    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'add_comment')
    def test_github_failed_rebase(self, m_comment, m_body):
        m_body.return_value = '@{} rebase'.format(self.repo.user.username)
        subprocess.Popen = fake_popen_failure
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with('Automated rebase failed! Please rebase '
                                     'your pull request manually via the '
                                     'command line.\n\nError:\n'
                                     '```Command \'[\'git\', \'rebase\', '
                                     '\'master\']\' returned non-zero exit '
                                     'status 128.```')

    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'add_comment')
    def test_gitlab_failed_rebase(self, m_comment, m_body):
        m_body.return_value = '@{} rebase'.format(self.repo.user.username)
        subprocess.Popen = fake_popen_failure
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gitlab_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with('Automated rebase failed! Please rebase '
                                     'your pull request manually via the '
                                     'command line.\n\nError:\n'
                                     '```Command \'[\'git\', \'rebase\', '
                                     '\'master\']\' returned non-zero exit '
                                     'status 128.```')

    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'add_comment')
    def test_github_successful_rebase(self, m_comment, m_body):
        m_body.return_value = '@{} rebase'.format(self.repo.user.username)
        subprocess.Popen = fake_popen_success
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with('Automated rebase was successful!')

    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'add_comment')
    def test_gitlab_successful_rebase(self, m_comment, m_body):
        m_body.return_value = '@{} rebase'.format(self.repo.user.username)
        subprocess.Popen = fake_popen_success
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gitlab_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with('Automated rebase was successful!')
