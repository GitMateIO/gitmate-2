from rest_framework import status
from rest_framework.reverse import reverse

from gitmate_config.tests.test_base import GitmateTestCase
from gitmate_config.models import Repository
from gitmate_config.views import UserViewSet
from django.contrib.auth.models import User


class TestApi(GitmateTestCase):

    def setUp(self):
        super().setUp()

        self.user_detail_url = reverse('api:users-detail',
                                       args=('me'))
        self.user_detail = UserViewSet.as_view(actions={
            'patch': 'partial_update',
            'put': 'update',
            'get': 'retrieve',
            'delete': 'destroy'
        })

    def test_retrieve(self):
        get_user_request = self.factory.get(self.user_detail_url)
        get_user_request.user = self.user
        response = self.user_detail(get_user_request, pk='me')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'username': 'john',
            'email': 'john.appleseed@example.com',
            'first_name': 'John',
            'last_name': 'Appleseed'
        })

    def test_update(self):
        update_user_request = self.factory.patch(
            self.user_detail_url,
            {'email': 'julian.assange@wikileaks.com'})
        update_user_request.user = self.user
        response = self.user_detail(update_user_request, pk='me')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'],
                         'julian.assange@wikileaks.com')

    def test_update_others(self):
        user = User.objects.create_user(
            email='lost@inthewoods.com',
            username='maya',
            first_name='Maya',
            last_name='Penellope'
        )
        update_user_request = self.factory.patch(
            self.user_detail_url,
            {'username': 'maya_is_lost'})
        # logging in as 'john' and trying to change 'maya'
        update_user_request.user = self.user
        response = self.user_detail(update_user_request, pk=user.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_user_single_admin(self):
        destroy_user_request = self.factory.delete(self.user_detail_url)
        destroy_user_request.user = self.user
        response = self.user_detail(destroy_user_request, pk='me')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Repository.objects.filter(user=self.user).count(), 0)

    def test_destroy_user_multiple_admin(self):
        # create a user and add him as an admin for self.repo
        user = User.objects.create_user(
            email='bruce@waynetech.com',
            username='the_dark_knight',
            first_name='Bruce',
            last_name='Wayne')

        self.repo.admins.add(user)
        self.repo.save()

        destroy_user_request = self.factory.delete(self.user_detail_url)
        destroy_user_request.user = self.user
        response = self.user_detail(destroy_user_request, pk='me')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # verifying that all user shared repos weren't deleted
        self.assertNotEqual(
            Repository.objects.filter(admins__in=[user]).count(), 0)

        # verifying the new operating user of self.repo
        self.assertEqual(
            Repository.objects.filter(admins__in=[user]).first().user, user)
