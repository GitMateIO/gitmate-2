"""
This file contains the test cases for approver plugin and its responders.
"""
from os import environ

from unittest.mock import patch
from unittest.mock import PropertyMock
from rest_framework import status
from IGitt.GitHub.GitHubCommit import GitHubCommit
from IGitt.GitLab.GitLabCommit import GitLabCommit
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.CommitStatus import Status

from gitmate_config.tests.test_base import GitmateTestCase


class TestGitmateApprover(GitmateTestCase):
    def setUp(self):
        super().setUpWithPlugin('approver')

        self.settings = [
            {
                'name': 'approver',
                'settings': {
                    'status_labels': 'WIP, process/pending_review',
                    'approved_label': 'approved',
                }
            }
        ]
        self.repo.set_plugin_settings(self.settings)
        self.gl_repo.set_plugin_settings(self.settings)

    @patch.object(GitHubCommit, 'combined_status',
                  new_callable=PropertyMock, return_value=Status.SUCCESS)
    @patch.object(GitHubMergeRequest, 'labels',
                  new_callable=PropertyMock, return_value={'WIP', 'bug'})
    def test_github_success_on_head_commit(self, m_labels, m_status):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 7},
            'action': 'opened'
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # now check the labels on status change
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'commit': {'sha': 'f6d2b7c66372236a090a2a74df2e47f42a54456b'}
        }
        response = self.simulate_github_webhook_call('status', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        # adds approved_label and removes status_labels
        m_labels.assert_called_with({'approved', 'bug'})

    @patch.object(GitLabCommit, 'combined_status',
                  new_callable=PropertyMock, return_value=Status.SUCCESS)
    @patch.object(GitLabMergeRequest, 'labels',
                  new_callable=PropertyMock, return_value={'WIP', 'bug'})
    def test_gitlab_success_on_head_commit(self, m_labels, m_status):
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 2
            }
        }
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # now check the labels on status change
        data = {
            'project': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
            'commit': {'id': '99f484ae167dcfcc35008ba3b5b564443d425ee0'}
        }
        response = self.simulate_gitlab_webhook_call('Pipeline Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        # adds approved_label and removes status_labels
        m_labels.assert_called_with({'approved', 'bug'})

    @patch.object(GitHubMergeRequest, 'labels',
                  new_callable=PropertyMock, return_value={'WIP', 'approved'})
    def test_github_failure_on_head_commit(self, m_labels):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 110},
            'action': 'synchronize'
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # now check the labels on status change
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'commit': {'sha': '91aaff6db9564480bf340c618c7ced4623c5be2e'}
        }
        response = self.simulate_github_webhook_call('status', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        # won't change any labels, removes approved_label if present
        m_labels.assert_called_with({'WIP'})

    @patch.object(GitLabMergeRequest, 'labels',
                  new_callable=PropertyMock, return_value={'WIP', 'approved'})
    def test_gitlab_failure_on_head_commit(self, m_labels):
        data = {
            'object_attributes': {
                'target': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
                'action': 'open',
                'iid': 24
            }
        }
        response = self.simulate_gitlab_webhook_call(
            'Merge Request Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # now check the labels on status change
        data = {
            'project': {'path_with_namespace': environ['GITLAB_TEST_REPO']},
            'commit': {'id': '8c31d04e826dc38e6b3e74143f83f9890b89c71c'}
        }
        response = self.simulate_gitlab_webhook_call('Pipeline Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        m_labels.assert_called()
        # adds approved_label and removes status_labels
        m_labels.assert_called_with({'WIP'})
