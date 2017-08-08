from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.CommitStatus import CommitStatus
from IGitt.Interfaces.CommitStatus import Status
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestAck(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('ack')
        self.gh_comment_data = {
            'repository': {'full_name': self.repo.full_name},
            'issue': {'number': 7, 'pull_request': {}},
            'comment': {'id': 0},
            'action': 'created'
        }
        self.gh_pr_data = {
            'repository': {'full_name': self.repo.full_name},
            'pull_request': {'number': 7},
            'action': 'opened'
        }
        self.gl_comment_data = {
            'project': {'path_with_namespace': self.gl_repo.full_name},
            'object_attributes': {
                'action': 'open',
                'id': 25,
                'iid': 0,
                'noteable_type': 'MergeRequest'
            },
            'merge_request': {'iid': 25}
        }
        self.gl_pr_data = {
            'object_attributes': {
                'target': {'path_with_namespace': self.gl_repo.full_name},
                'action': 'update',
                'oldrev': 'areallylongrandomshayoudontneedtocareabout',
                'iid': 25
            }
        }
        self.gh_token = GitHubToken(environ['GITHUB_TEST_TOKEN'])
        self.gl_token = GitLabOAuthToken(environ['GITLAB_TEST_TOKEN'])
        self.gh_commit = GitHubCommit(
            self.gh_token, self.repo.full_name,
            'f6d2b7c66372236a090a2a74df2e47f42a54456b')
        self.gl_commit = GitLabCommit(
            self.gl_token, self.gl_repo.full_name,
            'f6d2b7c66372236a090a2a74df2e47f42a54456b')

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_ack(
            self, m_set_status, m_get_statuses, m_sha, m_body, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'ack f6d2b7c'
        m_commits.return_value = tuple([self.gh_commit])
        response = self.simulate_github_webhook_call('pull_request',
                                                     self.gh_pr_data)
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.gh_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.SUCCESS review/gitmate/manual/pr
        # Status.SUCCESS review/gitmate/manual
        # Status.SUCCESS review/gitmate/manual/pr
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.SUCCESS, 'review/gitmate/manual/pr'),
                          (Status.SUCCESS, 'review/gitmate/manual'),
                          (Status.SUCCESS, 'review/gitmate/manual/pr')])

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_unack(
            self, m_set_status, m_get_statuses, m_sha, m_body, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'unack f6d2b7c'
        m_commits.return_value = tuple([self.gh_commit])
        response = self.simulate_github_webhook_call('pull_request',
                                                     self.gh_pr_data)
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.gh_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.FAILED review/gitmate/manual/pr This PR needs work
        # Status.FAILED review/gitmate/manual This commit needs work.
        # Status.FAILED review/gitmate/manual/pr This PR needs work
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.FAILED, 'review/gitmate/manual/pr'),
                          (Status.FAILED, 'review/gitmate/manual'),
                          (Status.FAILED, 'review/gitmate/manual/pr')])

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_pending_pr_open_event(
            self, m_set_status, m_get_statuses, m_sha, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'some/other/review', 'https://some/other/ci'),)
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_commits.return_value = tuple([self.gh_commit])
        response = self.simulate_github_webhook_call('pull_request',
                                                     self.gh_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 2 calls to be made as follows
        # Status.PENDING review/gitmate/manual This commit needs review.
        # Status.PENDING review/gitmate/manual/pr This PR needs review
        self.assertEqual(m_set_status.call_count, 2)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.PENDING, 'review/gitmate/manual'),
                          (Status.PENDING, 'review/gitmate/manual/pr')])

    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'get_statuses')
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_ack(
            self, m_set_status, m_get_statuses, m_sha, m_body, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'ack f6d2b7c'
        m_commits.return_value = tuple([self.gl_commit])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gl_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])

        # 3 calls to be made as follows
        # Status.SUCCESS review/gitmate/manual/pr
        # Status.SUCCESS review/gitmate/manual
        # Status.SUCCESS review/gitmate/manual/pr
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.SUCCESS, 'review/gitmate/manual/pr'),
                          (Status.SUCCESS, 'review/gitmate/manual'),
                          (Status.SUCCESS, 'review/gitmate/manual/pr')])

    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'get_statuses')
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_unack(
            self, m_set_status, m_get_statuses, m_sha, m_body, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'unack f6d2b7c'
        m_commits.return_value = tuple([self.gl_commit])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gl_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.FAILED review/gitmate/manual/pr This PR needs work
        # Status.FAILED review/gitmate/manual This commit needs work.
        # Status.FAILED review/gitmate/manual/pr This PR needs work
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.FAILED, 'review/gitmate/manual/pr'),
                          (Status.FAILED, 'review/gitmate/manual'),
                          (Status.FAILED, 'review/gitmate/manual/pr')])
