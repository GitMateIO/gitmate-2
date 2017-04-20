from hashlib import sha1
import hmac
from os import environ
from unittest import TestCase
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_hooks import ResponderRegistrar
from gitmate_hooks.views import github_webhook_receiver


@pytest.mark.django_db(transaction=False)
class TestWebhookReceivers(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.key = settings.GITHUB_WEBHOOK_SECRET
        self.user = User.objects.create_user(
            username='john',
            email='john.appleseed@example.com',
            first_name='John',
            last_name='Appleseed'
        )

        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.set_extra_data({
            'access_token': environ['GITHUB_TEST_TOKEN']
        })
        self.auth.save()

        self.repo = Repository(
            active=True,
            user=self.user,
            full_name=environ['GITHUB_TEST_REPO'],
            provider=Providers.GITHUB.value)
        self.repo.save()

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
            ResponderRegistrar._responders = {}

            response = github_webhook_receiver(request)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
