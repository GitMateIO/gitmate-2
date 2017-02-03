from unittest import TestCase

from django.contrib.auth.models import User
from django.test import RequestFactory
import pytest
from social_django.models import UserSocialAuth

from api.views import UserDetailsView
from api.views import UserOwnedRepositoriesView
from gitmate_config import Providers


@pytest.mark.django_db(transaction=False)
class TestApi(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            password="top_secret",
            first_name="John",
            last_name="Appleseed"
        )
        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.save()

    def test_details(self):
        request = self.factory.get('/api/me')

        # Explicitly setting the user to simulate logged in user and
        # generating the response via the api view.
        request.user = self.user
        response = UserDetailsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
                             'email': 'john.appleseed@example.com',
                             'first_name': 'John',
                             'last_name': 'Appleseed',
                             'username': 'john'
                         })

    def test_repositories(self):
        # Bad credentials
        self.auth.set_extra_data(extra_data={
            'access_token': 'themostwonderfulaccesstokenever'
        })
        self.auth.save()

        request = self.factory.get('/api/repos/?provider=github')
        request.user = self.user
        response = UserOwnedRepositoriesView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'error': 'Bad credentials',
            'status_code': 401
        })

        # Plugin not yet developed case
        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITLAB.value)
        self.auth.set_extra_data(extra_data={
            'access_token': 'themostwonderfulaccesstokenever'
        })
        self.auth.save()

        request = self.factory.get('/api/repos/?provider=gitlab')
        request.user = self.user
        response = UserOwnedRepositoriesView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'error': 'Plugin for host not yet developed',
            'status_code': 500
        })

        # Invalid Provider name
        request = self.factory.get('/api/repos/?provider=google')
        request.user = self.user
        response = UserOwnedRepositoriesView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'error': 'Requires a valid provider name',
            'status_code': 500
        })
