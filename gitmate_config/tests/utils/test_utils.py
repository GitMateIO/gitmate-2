from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_config.utils import get_user_if_exists
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitLab.GitLabUser import GitLabUser


class TestGitmateConfigUtils(GitmateTestCase):
    def test_get_user_if_exists(self):
        # It is none because we never created a database entry for the user:
        # `gitmate-test-user`
        gh_user = GitHubUser(self.repo.token, 'gitmate-test-user')
        self.assertIsNone(get_user_if_exists(gh_user))

        # Mocking the exact entry from database, to get proper return value
        gl_user = GitLabUser(self.repo.token, 2)
        self.assertIsNotNone(get_user_if_exists(gl_user))
