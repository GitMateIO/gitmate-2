from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import IntegrityError
from django.db import models
from django.test import TransactionTestCase
import pytest

from gitmate_config.models import Repository


@pytest.mark.django_db(transaction=False)
class TestRepository(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            email="john.appleseed@example.com",
            password="top_secret",
            first_name="John",
            last_name="Appleseed"
        )
        self.full_name = 'test'
        self.provider = 'example'

    def test__str__(self):
        repo = Repository(full_name=self.full_name,
                          provider=self.provider, user=self.user)
        assert str(repo) == self.full_name

    def test_defaults(self):
        repo = Repository(user=self.user)
        # checking default values
        assert not repo.active
        assert repo.full_name is None
        assert repo.provider is None
        # Don't allow none objects to be saved
        with pytest.raises(IntegrityError):
            repo.save()

    def test_validation(self):
        repo = Repository(user=self.user)
        # don't allow empty strings
        repo.full_name = ''
        repo.provider = ''
        with pytest.raises(ValidationError):
            repo.full_clean()

    def test_user(self):
        repo = Repository(full_name=self.full_name, provider=self.provider)
        # Don't allow saving if not linked to a user
        with pytest.raises(ValidationError):
            repo.full_clean()
        with pytest.raises(IntegrityError):
            repo.save()
