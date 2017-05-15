from hashlib import sha1
import hmac
import os

from django.contrib.auth.models import User
from django.test import TransactionTestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_hooks.views import github_webhook_receiver


class GitmateTestCase(TransactionTestCase):
    """
    A base class for setting up a dummy user, request factory and a repo for
    the user.
    """

    def setUp(self, active: bool=False):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            username='john',
            email='john.appleseed@example.com',
            first_name='John',
            last_name='Appleseed'
        )

        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN']
        })
        self.auth.save()

        self.repo = Repository(
            user=self.user,
            full_name=os.environ['GITHUB_TEST_REPO'],
            provider=Providers.GITHUB.value,
            active=active)
        self.repo.save()

    def setUpWithPlugin(self, name: str):
        self.plugin = Plugin(name=name)
        self.plugin_module = self.plugin.import_module()
        self.plugin.save()

        GitmateTestCase.setUp(self)

        self.repo.plugins.add(self.plugin)
        self.repo.active = True
        self.repo.save()

    def simulate_github_webhook_call(self, event: str, data: dict):
        request = self.factory.post(
            reverse('webhooks:github'), data, format='json')
        hashed = hmac.new(
            bytes(os.environ['GITHUB_WEBHOOK_SECRET'], 'utf-8'),
            request.body,
            sha1)
        signature = 'sha1=' + hashed.hexdigest()
        request.META.update({
            'HTTP_X_HUB_SIGNATURE': signature,
            'HTTP_X_GITHUB_EVENT': event,
        })

        return github_webhook_receiver(request)
