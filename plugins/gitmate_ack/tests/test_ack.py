from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubComment import GitHubComment
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitLab import GitLabOAuthToken
from IGitt.GitLab.GitLabComment import GitLabComment
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.GitLab.GitLabRepository import GitLabRepository
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.CommitStatus import CommitStatus
from IGitt.Interfaces.CommitStatus import Status
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestAck(GitmateTestCase):

    def setUp(self):
        super().setUpWithPlugin('ack')
        self.gh_comment_data = {
            'repository': {'full_name': self.repo.full_name, 'id': 49558751},
            'issue': {'number': 7, 'pull_request': {}},
            'comment': {'id': 0},
            'action': 'created'
        }
        self.gh_pr_data = {
            'repository': {'full_name': self.repo.full_name, 'id': 49558751},
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
    @patch.object(GitHubMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_ack_with_special_chars(
        self, m_set_status, m_get_statuses, m_sha, m_get_perms, m_author,
        m_body, m_head, m_commits
    ):
        self.repo.set_plugin_settings([{
            'name': 'ack',
            'settings': {
                'ack_strs': r'bot\ack, bot\accept'
            }
        }])

        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = r'bot\accept f6d2b7c'
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitHubUser(self.gh_token, self.user.username)
        m_head.return_value = self.gh_commit
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
    @patch.object(GitHubMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_ack(
        self, m_set_status, m_get_statuses, m_sha, m_get_perms, m_author,
        m_body, m_head, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'ack f6d2b7c'
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitHubUser(self.gh_token, self.user.username)
        m_head.return_value = self.gh_commit
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
    @patch.object(GitHubMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_unack(
        self, m_set_status, m_get_statuses, m_sha, m_get_perms, m_author,
        m_body, m_head, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'unack f6d2b7c'
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitHubUser(self.gh_token, self.user.username)
        m_head.return_value = self.gh_commit
        m_commits.return_value = tuple([self.gh_commit])
        response = self.simulate_github_webhook_call('pull_request',
                                                     self.gh_pr_data)
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.gh_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.FAILED review/gitmate/manual/pr
        # Status.FAILED review/gitmate/manual
        # Status.FAILED review/gitmate/manual/pr
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.FAILED, 'review/gitmate/manual/pr'),
                          (Status.FAILED, 'review/gitmate/manual'),
                          (Status.FAILED, 'review/gitmate/manual/pr')])

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_pending_pr_open_event(
            self, m_set_status, m_get_statuses, m_sha, m_head, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'some/other/review', 'https://some/other/ci'),)
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_head.return_value = self.gh_commit
        m_commits.return_value = tuple([self.gh_commit])
        response = self.simulate_github_webhook_call('pull_request',
                                                     self.gh_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 2 calls to be made as follows
        # Status.PENDING review/gitmate/manual
        # Status.PENDING review/gitmate/manual/pr
        self.assertEqual(m_set_status.call_count, 2)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.PENDING, 'review/gitmate/manual'),
                          (Status.PENDING, 'review/gitmate/manual/pr')])

    @patch.object(GitLabMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_new_head(self, m_set_status, m_commits, m_head):
        # First MR Sync
        m_head.return_value = self.gl_commit
        m_commits.return_value = tuple([self.gl_commit])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add a commit on top, now the one before (self.gl_commit) should get a
        # passing PR state because that's outdated and shouldn't block merges.
        new_head = GitLabCommit(self.gl_token, self.gl_repo.full_name,
                                '9ba5b704f5866e468ec2e639fa893ae4c129f2ad')
        m_head.return_value = new_head
        m_commits.return_value = tuple([self.gl_commit, new_head])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        states = sum([list(args) for args, _ in m_set_status.call_args_list],
                     [])
        self.assertIn((Status.SUCCESS, 'review/gitmate/manual/pr',
                       'Outdated. Check 9ba5b70 instead.'),
                      [(state.status, state.context, state.description)
                       for state in states])

    @patch.object(GitLabMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'set_status')
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'author', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'get_permission_level')
    def test_gitlab_delete_old_acks(self, m_get_perms, m_author, m_body,
                                    m_set_status, m_commits, m_head):
        # First MR Sync, create value in ack
        m_head.return_value = self.gl_commit
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitLabUser(self.gl_token, 0)
        m_commits.return_value = tuple([self.gl_commit])
        m_body.return_value = 'unack ' + self.gl_commit.sha
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gl_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.PENDING, 'review/gitmate/manual'),
                          (Status.PENDING, 'review/gitmate/manual/pr'),
                          (Status.FAILED, 'review/gitmate/manual'),
                          (Status.FAILED, 'review/gitmate/manual/pr')])
        m_set_status.reset_mock()

        # Completely new commit, SHA for old commit should be removed
        new_head = GitLabCommit(self.gl_token, self.gl_repo.full_name,
                                '9ba5b704f5866e468ec2e639fa893ae4c129f2ad')
        m_head.return_value = new_head
        m_commits.return_value = tuple([new_head])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])

        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.PENDING, 'review/gitmate/manual'),
                          (Status.PENDING, 'review/gitmate/manual/pr')])

    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'unified_diff', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'message', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'get_statuses')
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_unmodified_commit(
        self, m_set_status, m_get_statuses, m_sha, m_message, m_diff, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'Good to go!',
                         'review/gitmate/manual', 'https://gitmate.io'),)
        m_diff.return_value = ('--- a/README.md\n'
                               '+++ b/README.md\n'
                               '@@ -1,2 +1,4 @@\n'
                               ' # test\n'
                               ' a test repo\n'
                               '+\n'
                               '+a commiit that can one acknowledge')
        m_message.return_value = 'Update README.md'
        m_commits.return_value = tuple([self.gl_commit])
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # resyncing merge request with a new unmodified commit
        m_sha.return_value = '9ba5b704f5866e468ec2e639fa893ae4c129f2ad'
        m_commits.return_value = tuple([GitLabCommit(
            self.gl_token, self.gl_repo.full_name, m_sha.return_value)])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.SUCCESS review/gitmate/manual/pr
        # Status.SUCCESS review/gitmate/manual
        # Status.SUCCESS review/gitmate/manual/pr
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.SUCCESS, 'review/gitmate/manual/pr'),
                          (Status.SUCCESS, 'review/gitmate/manual'),
                          (Status.SUCCESS, 'review/gitmate/manual/pr')])

    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'author', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'get_permission_level')
    @patch.object(GitLabCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'get_statuses')
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_ack(
            self, m_set_status, m_get_statuses, m_sha, m_get_perms, m_author,
            m_body, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_body.return_value = 'ack f6d2b7c'
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitLabUser(self.gl_token, 0)
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
    @patch.object(GitLabComment, 'author', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'get_permission_level')
    @patch.object(GitLabCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitLabCommit, 'get_statuses')
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_unack(
            self, m_set_status, m_get_statuses, m_sha, m_get_perms, m_author,
            m_body, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitLabUser(self.gl_token, 0)
        m_body.return_value = 'unack f6d2b7c'
        m_commits.return_value = tuple([self.gl_commit])
        response = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                                     self.gl_pr_data)
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gl_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.FAILED review/gitmate/manual/pr
        # Status.FAILED review/gitmate/manual
        # Status.FAILED review/gitmate/manual/pr
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.FAILED, 'review/gitmate/manual/pr'),
                          (Status.FAILED, 'review/gitmate/manual'),
                          (Status.FAILED, 'review/gitmate/manual/pr')])

    @patch.object(GitHubMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitHubMergeRequest, 'head', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'body', new_callable=PropertyMock)
    @patch.object(GitHubComment, 'author', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_permission_level')
    @patch.object(GitHubCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitHubCommit, 'get_statuses')
    @patch.object(GitHubCommit, 'set_status')
    def test_github_comment_after_sync_no_data_in_db(
        self, m_set_status, m_get_statuses, m_sha, m_get_perms, m_author,
        m_body, m_head, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.FAILED, 'Terrible issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_get_perms.return_value = AccessLevel.CAN_WRITE
        m_author.return_value = GitHubUser(self.gh_token, self.user.username)
        m_body.return_value = 'unack f6d2b7c'
        m_head.return_value = self.gh_commit
        m_commits.return_value = tuple([self.gh_commit])
        response = self.simulate_github_webhook_call('issue_comment',
                                                     self.gh_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        args = sum([list(args) for args, _ in m_set_status.call_args_list], [])
        # 3 calls to be made as follows
        # Status.FAILED review/gitmate/manual/pr
        # Status.FAILED review/gitmate/manual
        # Status.FAILED review/gitmate/manual/pr
        self.assertEqual(m_set_status.call_count, 3)
        self.assertEqual([(arg.status, arg.context) for arg in args],
                         [(Status.FAILED, 'review/gitmate/manual/pr'),
                          (Status.FAILED, 'review/gitmate/manual'),
                          (Status.FAILED, 'review/gitmate/manual/pr')])

    @patch.object(GitLabMergeRequest, 'commits', new_callable=PropertyMock)
    @patch.object(GitLabMergeRequest, 'add_comment')
    @patch.object(GitLabCommit, 'sha', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'author', new_callable=PropertyMock)
    @patch.object(GitLabComment, 'body', new_callable=PropertyMock)
    @patch.object(GitLabUser, 'username', new_callable=PropertyMock)
    @patch.object(GitLabRepository, 'get_permission_level')
    @patch.object(GitLabCommit, 'get_statuses')
    @patch.object(GitLabCommit, 'set_status')
    def test_gitlab_ack_without_minimum_access_level(
            self, _, m_get_statuses, m_get_perms, m_username, m_body, m_author,
            m_sha, m_add_comment, m_commits
    ):
        m_get_statuses.return_value = (
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/gitmate/manual', 'https://gitmate.io'),
            CommitStatus(Status.SUCCESS, 'No issues',
                         'review/somewhere/else', 'https://some/url'))
        m_sha.return_value = 'f6d2b7c66372236a090a2a74df2e47f42a54456b'
        m_get_perms.return_value = AccessLevel.CAN_VIEW
        m_username.return_value = self.user.username
        m_body.return_value = 'unack f6d2b7c'
        m_author.return_value = GitLabUser(self.gl_token, 0)
        m_commits.return_value = tuple([self.gl_commit])
        _ = self.simulate_gitlab_webhook_call('Merge Request Hook',
                                              self.gl_pr_data)
        response = self.simulate_gitlab_webhook_call('Note Hook',
                                                     self.gl_comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        m_add_comment.assert_called_once_with(
            'Sorry @{}, you do not have the necessary permission levels to '
            'perform the action.'.format(self.user.username))
