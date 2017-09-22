from gitmate_config.models import Organization
from gitmate_config.tests.test_base import GitmateTestCase


class TestOrganization(GitmateTestCase):

    def setUp(self):
        super().setUp()
        self.glorg = Organization(
            name='test_org',
            primary_user=self.user,
            provider='gitlab',
        )
        self.glorg.save()
        self.ghorg = Organization(
            name='test_org',
            primary_user=self.user,
            provider='github',
        )
        self.ghorg.save()

    def test_from_igitt(self):
        self.assertEqual(Organization.from_igitt_org(self.ghorg.igitt_org),
                         self.ghorg)
        self.assertEqual(Organization.from_igitt_org(self.glorg.igitt_org),
                         self.glorg)

    def test_str(self):
        self.assertEqual(str(self.glorg), 'gitlab:test_org')
