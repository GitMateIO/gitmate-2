import os
from unittest import TestCase

from django.contrib.auth.models import User
from IGitt.Interfaces.Repository import Repository as IGittRepository
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from social_django.models import UserSocialAuth

from gitmate_config import Providers
from gitmate_config.models import Repository
from gitmate_config.views import RepositoryViewSet


@pytest.mark.django_db(transaction=False)
class TestRepositories(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            password="top_secret",
            first_name="John",
            last_name="Appleseed"
        )
        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITHUB.value)
        self.auth.set_extra_data({
            'access_token': os.environ['GITHUB_TEST_TOKEN']
        })
        self.auth.save()

        self.repo_list = RepositoryViewSet.as_view(actions={'get': 'list'})
        self.repo_list_url = reverse('api:repository-list')

        self.repo_detail = RepositoryViewSet.as_view(
            actions={'patch': 'partial_update', 'put': 'update'},
        )

    def test_get_repos(self):
        get_repos_request = self.factory.get(self.repo_list_url)
        response = self.repo_list(get_repos_request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        get_repos_request.user = self.user
        response = self.repo_list(get_repos_request)
        self.assertIn(os.environ['GITHUB_TEST_REPO'],
                      [elem['full_name'] for elem in response.data])

    def test_activate_repo(self):
        repo = Repository(
            user=self.user,
            provider='github',
            full_name=os.environ['GITHUB_TEST_REPO'],
            active=False
        )
        repo.save()
        igitt_repo = repo.igitt_repo()
        # Activate repo!
        url = reverse('api:repository-detail', args=(repo.pk,))
        activate_repo_request = self.factory.patch(
            url,
            {'active': True},
            HTTP_HOST='testing.com',
        )
        activate_repo_request.user = self.user
        response = self.repo_detail(activate_repo_request, pk=repo.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('https://testing.com/webhooks/github', igitt_repo.hooks)

        deactivate_repo_request = self.factory.patch(
            url,
            {'active': False},
            HTTP_HOST='testing.com',
        )
        deactivate_repo_request.user = self.user
        response = self.repo_detail(deactivate_repo_request, pk=repo.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('https://testing.com/webhooks/github',
                         igitt_repo.hooks)

    def test_igitt_repo_creation(self):
        repo = Repository(
            user=self.user,
            provider='github',
            full_name=os.environ['GITHUB_TEST_REPO'],
            active=False
        ).igitt_repo()
        self.assertIsInstance(repo, IGittRepository)

    def test_not_implemented_igitt_repo_creation(self):
        self.auth = UserSocialAuth(
            user=self.user, provider=Providers.GITLAB.value)
        self.auth.set_extra_data({
            'access_token': 'stupidshit'
        })
        self.auth.save()

        with self.assertRaises(NotImplementedError):
            repo = Repository(
                user=self.user,
                provider='gitlab',
                full_name='some_repo',
                active=False
            ).igitt_repo()
