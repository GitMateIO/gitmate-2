from hashlib import sha1
import hmac
from os import environ
from unittest.mock import patch

from django.conf import settings
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_hooks.views import github_webhook_receiver


class TestWebhookReceivers(GitmateTestCase):

    def setUp(self):
        super().setUp(active=True)
        self.key = settings.GITHUB_WEBHOOK_SECRET

    def test_github_webhook_receiver_signature_match_failed(self):
        data = {'some-random-key': 'some-random-value'}
        request = self.factory.post('/webhooks/github', data, format='json')
        request.META.update({'HTTP_X_HUB_SIGNATURE': 'sha1=somerandomvalue'})
        response = github_webhook_receiver(request)
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_github_webhook_receiver_no_signature(self):
        data = {'some-random-key': 'some-random-value'}
        request = self.factory.post('/webhooks/github', data, format='json')

        response = github_webhook_receiver(request)
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_github_webhook_receiver_no_data_received(self):
        request = self.factory.post('/webhooks/github', format='json')

        response = github_webhook_receiver(request)
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_github_webhook_receiver_successful_pull_request_opened(self):
        data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
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
