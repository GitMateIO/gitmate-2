from rest_framework import status

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_config.views import UserDetailsView


class TestApi(GitmateTestCase):

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
