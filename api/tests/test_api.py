from unittest import TestCase

from django.contrib.auth.models import User
from django.test import RequestFactory
import pytest

from api.views import UserDetailsView


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

    def test_details(self):
        request = self.factory.get('/api/me')

        # Explicitly setting the user to simulate logged in user and
        # generating the response via the api view.
        request.user = self.user
        response = UserDetailsView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {
                             'user':
                             {
                                 'email': 'john.appleseed@example.com',
                                 'first_name': 'John',
                                 'last_name': 'Appleseed',
                                 'username': 'john'
                             }
                         })
