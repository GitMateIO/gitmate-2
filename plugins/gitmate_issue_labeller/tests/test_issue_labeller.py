from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from IGitt.GitHub.GitHubIssue import GitHubIssue
from IGitt.GitLab.GitLabIssue import GitLabIssue


class TestIssueLabeller(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('issue_labeller')

    @patch.object(GitHubIssue, 'description', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'title', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'available_labels', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    def test_github(self, m_labels, m_avail_labels, m_title, m_desc):
        # needed for the igitt object locking
        GitHubIssue._repository = environ['GITHUB_TEST_REPO']
        GitHubIssue.number = 2
        # clear all the labels
        m_labels.return_value = set()

        # give some random labels
        m_avail_labels.return_value = ['apples', 'spaceships', 'bears']

        # set some random summary
        m_title.return_value = 'Shape of you'
        m_desc.return_value = 'Make coala bears sing this song!'

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'issue': {'number': 2},
            'action': 'opened'
        }

        response = self.simulate_github_webhook_call('issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'bears'})

    @patch.object(GitLabIssue, 'description', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'title', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'available_labels', new_callable=PropertyMock)
    @patch.object(GitLabIssue, 'labels', new_callable=PropertyMock)
    def test_gitlab(self, m_labels, m_avail_labels, m_title, m_desc):
        # needed for the igitt object locking
        GitLabIssue._repository = environ['GITHUB_TEST_REPO']
        GitLabIssue.number = 2
        # clear all the labels
        m_labels.return_value = set()

        # give some random labels
        m_avail_labels.return_value = ['apples', 'spaceships', 'bears']

        # set some random summary
        m_title.return_value = 'Shape of you'
        m_desc.return_value = 'Make coala bears sing this song!'

        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 2
            }
        }

        response = self.simulate_gitlab_webhook_call('Issue Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'bears'})
