import os
from unittest import TestCase

from django.contrib.auth.models import User
import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from api.views import UserDetailsView
from api.views import UserOwnedRepositoriesView
from gitmate_config import Providers
from gitmate_config.models import Repository


@pytest.mark.django_db(transaction=False)
class TestApi(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            first_name="John",
            last_name="Appleseed"
        )

        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.save()

        self.repo = Repository(
            user=self.user,
            full_name=os.environ['GITHUB_TEST_REPO'],
            provider=Providers.GITHUB.value)
        self.repo.save()

    def test_details(self):
        request = self.factory.get('/api/me')

        # Explicitly setting the user to simulate logged in user and
        # generating the response via the api view.
        request.user = self.user
        response = UserDetailsView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
                             'email': 'john.appleseed@example.com',
                             'first_name': 'John',
                             'last_name': 'Appleseed',
                             'username': 'john'
                         })

    def test_repositories_bad_credentials(self):
        # Bad credentials
        self.auth.set_extra_data(extra_data={
            'access_token': 'themostwonderfulaccesstokenever'
        })
        self.auth.save()

        request = self.factory.get('/api/repos/')
        request.user = self.user
        response = UserOwnedRepositoriesView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {
            'error': 'Bad credentials'
        })

    def test_repositories_successful(self):
        # Correct credentials
        self.auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN']
        })
        self.auth.save()

        request = self.factory.get('/api/repos/')
        request.user = self.user
        response = UserOwnedRepositoriesView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            Providers.GITHUB.value: {os.environ['GITHUB_TEST_REPO']}
        })
