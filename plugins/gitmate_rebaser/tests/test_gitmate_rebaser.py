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
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces import AccessLevel

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_config.tests.test_base import StreamMock


PopenResult = namedtuple('ret', 'stdout wait')


def fake_popen_success(cmd, **kwargs):
    if 'run.py' in cmd:
        return PopenResult(StreamMock('{"status": "success"}'),
                           lambda *args, **kwargs: None)


def fake_popen_failure(cmd, **kwargs):
    if 'run.py' in cmd:
        return PopenResult(
            StreamMock(
                '{"status": "error", "error": "Command \'[\'git\', \'rebase\''
                ', \'master\']\' returned non-zero exit status 128."}'),
            lambda *args, **kwargs: None)


class TestGitmateRebaser(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('rebaser')
        self.repo.set_plugin_settings([{
            'name': 'rebaser',
            'settings': {
                'enable_rebase': True
            }
        }])
        self.gl_repo.set_plugin_settings([{
            'name': 'rebaser',
            'settings': {
                'enable_rebase': True
            }
        }])
        self.github_data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
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
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    def test_github_failed_rebase(
            self, m_get_perm, m_author, m_comment, m_body
    ):
        m_body.return_value = '@{} rebase'.format(
            self.repo.user.username.upper())
        m_author.return_value = GitHubUser(
            self.repo.token, self.repo.user.username)
        m_get_perm.return_value = AccessLevel.CAN_READ
        subprocess.Popen = fake_popen_failure
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with('Automated rebase failed! Please rebase '
                                     'your pull request manually via the '
                                     'command line.\n\nReason:\n'
                                     '```\nCommand \'[\'git\', \'rebase\', '
                                     '\'master\']\' returned non-zero exit '
                                     'status 128.\n```')

    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'add_comment')
    @patch.object(GitLabComment, 'author', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'get_permission_level')
    def test_gitlab_failed_rebase(
            self, m_get_perm, m_author, m_comment, m_body
    ):
        m_body.return_value = '@{} rebase'.format(self.repo.user.username)
        m_author.return_value = GitLabUser(self.repo.token, 0)
        m_get_perm.return_value = AccessLevel.CAN_READ
        subprocess.Popen = fake_popen_failure
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gitlab_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with('Automated rebase failed! Please rebase '
                                     'your pull request manually via the '
                                     'command line.\n\nReason:\n'
                                     '```\nCommand \'[\'git\', \'rebase\', '
                                     '\'master\']\' returned non-zero exit '
                                     'status 128.\n```')

    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'add_comment')
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    def test_github_successful_rebase(
            self, m_get_perm, m_author, m_comment, m_body
    ):
        m_body.return_value = f'@{self.repo.user.username} rebase'
        m_author.return_value = GitHubUser(
            self.repo.token, self.repo.user.username)
        m_get_perm.return_value = AccessLevel.CAN_READ
        subprocess.Popen = fake_popen_success
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with(
            'Automated rebase with [GitMate.io](https://gitmate.io) was '
            'successful! :tada:')

    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'add_comment')
    @patch.object(GitLabComment, 'author', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'get_permission_level')
    def test_gitlab_successful_rebase(
            self, m_get_perm, m_author, m_comment, m_body
    ):
        m_body.return_value = '@{} rebase'.format(self.repo.user.username)
        m_author.return_value = GitLabUser(self.repo.token, 0)
        m_get_perm.return_value = AccessLevel.CAN_READ
        subprocess.Popen = fake_popen_success
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gitlab_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with(
            'Automated rebase with [GitMate.io](https://gitmate.io) was '
            'successful! :tada:')

    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'add_comment')
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    def test_github_unauthorized(
            self, m_get_perm, m_author, m_comment, m_body
    ):
        m_body.return_value = f'@{self.repo.user.username} rebase'
        m_author.return_value = GitHubUser(
            self.repo.token, self.repo.user.username)
        m_get_perm.return_value = AccessLevel.NONE
        subprocess.Popen = fake_popen_success
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.github_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_comment.assert_called_with(
            f'Hey @{self.repo.user.username}, you do not have the access to '
            'perform the rebase action with [GitMate.io](https://gitmate.io). '
            'Please ask a maintainer to give you access. :warning:')
