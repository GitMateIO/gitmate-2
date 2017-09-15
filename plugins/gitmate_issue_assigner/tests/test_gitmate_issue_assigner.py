from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitLab.GitLabIssue import GitLabIssue


class TestIssueAssigner(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('issue_assigner')

        self.settings = [
            {
                'name': 'issue_assigner',
                'settings': {
                    'keywords': {
                        'apples': 'apples',
                        'spaceships': 'spaceships, ',
                        'bears': 'bears',
                        'bear-related': 'bears, stupidshit',
                    },
                }
            }
        ]
        self.repo.set_plugin_settings(self.settings)
        self.gl_repo.set_plugin_settings(self.settings)

    @patch.object(GitHubIssue, 'description', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'title', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'assign')
    def test_github(self, m_assign, m_title, m_desc):
        # set some random summary
        m_title.return_value = 'Shape of you'
        m_desc.return_value = 'Make coala bears sing this song!'

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'issue': {'number': 104},
            'action': 'opened'
        }

        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_assign.assert_any_call('bear-related')
        m_assign.assert_any_call('bears')

    @patch.object(GitLabIssue, 'description', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'title', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'assign')
    def test_gitlab(self, m_assign, m_title, m_desc):
        # set some random summary
        m_title.return_value = 'Shape of you'
        m_desc.return_value = 'Make coala bears sing this song!'

        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 21
            }
        }

        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_assign.assert_any_call('bear-related')
        m_assign.assert_any_call('bears')
