import os
from unittest import TestCase

from django.contrib.auth.models import User
import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.views import ActivateRepositoryView


@pytest.mark.django_db(transaction=False)
class TestAddRepo(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            password="top_secret",
            first_name="John",
            last_name="Appleseed"
        )
        self.put_data = {
            'provider': Providers.GITHUB.value,
            'repository': os.environ['GITHUB_TEST_REPO'],
        }
        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN']
        })
        self.auth.save()

    def test_activate_repo_github_authorized(self):
        # GITHUB testing authorized access
        request = self.factory.put('/api/repo/add',
                                   self.put_data,
                                   HTTP_HOST='example.com')
        # mock the authentication
        request.user = self.user
        response = ActivateRepositoryView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {
            'user': self.user.id,
            'provider': self.put_data['provider'],
            'full_name': self.put_data['repository'],
            'active': True
        })

    def test_activate_repo_github_unauthorized(self):
        # GITHUB testing unauthorized access
        request = self.factory.put('/api/repo/add',
                                   self.put_data,
                                   HTTP_HOST='example.com')
        self.auth.set_extra_data({
            'access_token': "themostwonderfulaccesstokenever"
        })
        self.auth.save()
        request.user = self.user

        response = ActivateRepositoryView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {
            'error': "Bad credentials"
        })

    def test_activate_repo_gitlab_authorized(self):
        # GITLAB testing
        self.put_data['provider'] = Providers.GITLAB.value
        request = self.factory.put('/api/repo/add',
                                   self.put_data,
                                   HTTP_HOST='example.com')
        # mock the authentication via a user
        request.user = self.user
        response = ActivateRepositoryView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': "Invalid request"})
