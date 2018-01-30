from hashlib import sha1
import hmac
from os import environ
from unittest.mock import patch

from django.conf import settings
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from rest_framework import status
from rest_framework.response import Response

from gitmate_config.models import Installation
from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_hooks.views import github_webhook_receiver
from gitmate_hooks.decorators import signature_check


class TestWebhookReceivers(GitmateTestCase):
    active = True
    key = settings.WEBHOOK_SECRET

    def test_webhook_no_key_verification_off(self):

        @signature_check(None, 'some_check', 'HTTP_X_SIGNATURE')
        def receiver(*args, **kwargs):
            return Response(status=status.HTTP_200_OK)

        data = {'some-random-key': 'some-random-value'}
        request = self.factory.post('/webhooks/nowhere', data, format='json')
        response = receiver(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_github_webhook_receiver_signature_match_failed(self):
        data = {'some-random-key': 'some-random-value'}
        request = self.factory.post('/webhooks/github', data, format='json')
        request.META.update({'HTTP_X_HUB_SIGNATURE': 'sha1=somerandomvalue'})
        response = github_webhook_receiver(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_github_webhook_receiver_no_signature(self):
        data = {'some-random-key': 'some-random-value'}
        request = self.factory.post('/webhooks/github', data, format='json')
        response = github_webhook_receiver(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_github_webhook_receiver_no_data_received(self):
        request = self.factory.post('/webhooks/github', format='json')
        response = github_webhook_receiver(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_github_webhook_receiver_successful_pull_request_opened(self):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 0},
            'action': 'opened'
        }
        request = self.factory.post('/webhooks/github', data, format='json')
        hashed = hmac.new(bytes(self.key, 'utf-8'), request.body, sha1)
        signature = 'sha1=' + hashed.hexdigest()

        request.META.update({
            'HTTP_X_HUB_SIGNATURE': signature,
            'HTTP_X_GITHUB_EVENT': 'pull_request'
        })

        # Mocking the GitHubMergeRequest as no such pull request exists and
        # resetting all the responders to stop unnecessary actions during
        # testing phase.
        with patch.object(GitHubMergeRequest, '__init__', return_value=None):
            response = github_webhook_receiver(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gitlab_webhook_receiver_with_build_hook(self):
        data = {
            'repository': {'git_ssh_url': 'git@example.com:{}.git'.format(
                environ['GITLAB_TEST_REPO'])},
            'build_status': 'created',
            'commit': {'sha': 'somerandomshawewillneverseeanywherebuthere'}
        }
        response = self.simulate_gitlab_webhook_call('Build Hook', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_github_integration_webhook(self):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO'],
                           'id': 49558751},
            'pull_request': {'number': 0},
            'action': 'opened',
            'installation': {'id': 60731}
        }
        response = self.simulate_github_webhook_call('pull_request', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_github_installation_webhook_created_or_updated(self):
        # installation created webhook
        data = {
            'action': 'created',
            'installation': {'id': 11},
            'sender': {'login': self.user.username, 'id': 1},
            'repositories': [
                {'id': 49558751, 'full_name': self.repo.full_name}
            ]
        }
        response = self.simulate_github_webhook_call('installation', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verification
        self.repo.refresh_from_db()
        db_inst = Installation.objects.get(identifier=11, provider='github')
        self.assertIn(self.user, db_inst.admins.all())
        self.assertIn(self.repo, db_inst.repos.all())

        # repositories removed webhook
        data = {
            'action': 'removed',
            'installation': {'id': 11},
            'sender': {'login': self.user.username, 'id': 1},
            'repositories_removed': [
                {'id': 49558751, 'full_name': self.repo.full_name}
            ]
        }
        response = self.simulate_github_webhook_call(
            'installation_repositories', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verification
        self.repo.refresh_from_db()
        db_inst.refresh_from_db()
        self.assertNotIn(self.repo, db_inst.repos.all())

    def test_github_installation_webhook_deleted(self):
        # creating a sample object and testing for deletion
        db_inst = Installation.objects.create(identifier=12, provider='github')

        data = {
            'action': 'deleted',
            'installation': {'id': 12},
            'sender': {'login': self.repo.user.username, 'id': 1}
        }
        response = self.simulate_github_webhook_call('installation', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.assertRaises(Installation.DoesNotExist):
            db_inst.refresh_from_db()
