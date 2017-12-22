
from gitmate_config.enums import Providers
from gitmate_config.models import Installation
from gitmate_config.tests.test_base import GitmateTestCase


class TestInstallation(GitmateTestCase):

    def setUp(self):
        super().setUp()
        self.gh_inst = Installation.objects.create(
            provider=Providers.GITHUB.value,
            identifier=73666)

    def test_from_igitt(self):
        self.assertEqual(
            Installation.from_igitt_installation(
                self.gh_inst.igitt_installation),
            self.gh_inst)

    def test_token(self):
        self.assertRegexpMatches(self.gh_inst.token.value, 'v1\.[0-9a-f]{40}')
