import os
import shutil
from subprocess import PIPE
from subprocess import Popen
from subprocess import STDOUT
from tempfile import mkdtemp
from tempfile import mkstemp
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import PropertyMock

from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitHub.GitHubRepository import GitHubRepository
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


class TestBugSpotter(GitmateTestCase):

    @staticmethod
    def run_git_command(*args, stdin=None):
        pipe = Popen(' '.join(('git', ) + args),
                     shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        if stdin is not None:
            pipe.stdin.write(bytes(stdin, 'utf-8'))
            pipe.stdin.close()

    @staticmethod
    def git_change_stage_commit(msg, changes: dict):
        for file, content in changes.items():
            with open(file, 'w') as _file:
                _file.write(content)
                _file.close()
        TestBugSpotter.run_git_command('add', '.')
        TestBugSpotter.run_git_command('commit',
                                       '--file=-',
                                       stdin=msg)
        # sleep for a second so that bugspots has atleast some
        # time gap between commits
        from time import sleep
        sleep(1)

    def setUp(self):
        self.setUpWithPlugin('bug_spotter')

        self._old_cwd = os.getcwd()
        self.gitdir = mkdtemp()
        self.files = set()
        for i in range(10):
            _, filename = mkstemp(dir=self.gitdir)
            self.files.add(filename)

        os.chdir(self.gitdir)

        self.run_git_command('init')
        self.run_git_command('config', 'user.email pytest@gitmate.io')
        self.run_git_command('config', 'user.name pytest')

        self.git_change_stage_commit('Hello World\n',
                                     {f: 'bar' for f in self.files})
        self.git_change_stage_commit('Change bar to foo\nFix #1',
                                     {f: 'foo' for f in self.files})
        self.git_change_stage_commit('Change foo to foobar\nFix #2',
                                     {f: 'foobar' for f in self.files})

        os.chdir(self._old_cwd)

    def tearDown(self):
        shutil.rmtree(self.gitdir, ignore_errors=True)

    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubRepository, 'get_clone', autospec=True)
    @patch.object(GitHubMergeRequest, 'affected_files',
                  new_callable=PropertyMock)
    def test_github(self, m_aff_files, m_clone, m_labels):
        m_aff_files.return_value = {os.path.basename(f) for f in self.files}
        m_clone.return_value = (None, self.gitdir, )
        m_labels.return_value.add = MagicMock()

        data = {
            'repository': {'full_name': self.repo.full_name},
            'pull_request': {'number': 7},
            'action': 'synchronize'
        }
        response = self.simulate_github_webhook_call('pull_request', data)

        m_clone.assert_called()
        m_labels.assert_called()

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        m_labels().add.assert_called_with('review carefully!')
