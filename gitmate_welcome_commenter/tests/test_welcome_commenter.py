from hashlib import sha1
import hmac
from os import environ
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings
from django.test import TransactionTestCase
from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.Interfaces.Actions import MergeRequestActions
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_hooks import ResponderRegistrar
from gitmate_hooks.views import github_webhook_receiver


@override_settings(CELERY_ALWAYS_EAGER=True)
@pytest.mark.django_db(transaction=False)
class TestWelcomeCommenter(TransactionTestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.key = settings.GITHUB_WEBHOOK_SECRET

        self.plugin = Plugin(name='welcome_commenter')
        self.plugin_module = self.plugin.import_module()
        self.plugin.save()

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

        self.repo.plugins.add(self.plugin)
        self.repo.save()

        self.github_webhook_receive_url = reverse('webhooks:github')
        self.github_data = {
            'repository': {'full_name': environ['GITHUB_TEST_REPO']},
            'pull_request': {'number': 7},
            'action': 'opened'
        }

    @patch('IGitt.GitHub.GitHubIssue.GitHubIssue.add_comment', autospec=True)
    def test_github(self, mock_add_comment):
        webhook_request = self.factory.post(
            self.github_webhook_receive_url, self.github_data, format='json')

        hashed = hmac.new(bytes(self.key, 'utf-8'), webhook_request.body, sha1)
        signature = 'sha1=' + hashed.hexdigest()
        webhook_request.META.update({
            'HTTP_X_HUB_SIGNATURE': signature,
            'HTTP_X_GITHUB_EVENT': 'pull_request'
        })
        response = github_webhook_receiver(webhook_request)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        mock_add_comment.assert_called_once()
