from os import environ

from django.apps.registry import Apps

from gitmate_config.tests.test_base import MigrationTestCase


class RepositoryIdentifierMigrationTestCase(MigrationTestCase):
    app = 'gitmate_config'
    migrate_from = '0018_auto_20180130_0738'
    migrate_to = '0019_change_pk_to_identifier'

    def setUpBeforeMigration(self, apps: Apps):
        Repository = apps.get_model('gitmate_config', 'Repository')
        Installation = apps.get_model('gitmate_config', 'Installation')

        self.inst = Installation(provider='github', identifier=81451)
        self.inst.save()

        self.repo = Repository(
            provider='github',
            installation=self.inst,
            full_name=environ['GITHUB_TEST_REPO'])
        self.repo.save()

        Repository(provider='coala.io',
                   installation=self.inst,
                   full_name='some/fancy/name').save()

    def test_successful_migration(self):
        Repository = self.apps.get_model('gitmate_config', 'Repository')
        # ensure that there was no identifier before
        self.assertIsNone(self.repo.identifier)

        self.repo.refresh_from_db()

        # ensure that the idenfier was generated
        self.assertEqual(self.repo.identifier, 49558751)

        # ensure that the other repo is deleted
        self.assertEqual(Repository.objects.count(), 1)
