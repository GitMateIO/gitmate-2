from os import environ
from unittest.mock import patch
from unittest.mock import PropertyMock

from django.test import override_settings
from IGitt.GitHub.GitHubIssue import GitHubIssue
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase


@override_settings(CELERY_ALWAYS_EAGER=True)
class TestIssueLabeller(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('issue_labeller')

    @patch.object(GitHubIssue, 'description', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'title', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'available_labels', new_callable=PropertyMock)
    @patch.object(GitHubIssue, 'labels', new_callable=PropertyMock)
    @patch.object(GitHubIssue, '__init__', return_value=None)
    def test_github(self, m_issue, m_labels, m_avail_labels, m_title, m_desc):
        # clear all the labels
        m_labels.return_value = set()

        # give some random labels
        m_avail_labels.return_value = ['apples', 'spaceships', 'bears']

        # set some random summary
        m_title.return_value = 'Shape of you'
        m_desc.return_value = 'Make coala bears sing this song!'

        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'issue': {'number': 0},
            'action': 'opened'
        }

        response = self.simulate_github_webhook_call('issues', data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        m_labels.assert_called_with({'bears'})
