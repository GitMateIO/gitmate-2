from os import environ

from django.apps.registry import Apps

from gitmate_config.tests.test_base import MigrationTestCase


class RepositoryPluginFieldMigrationTestCase(MigrationTestCase):
    app = 'gitmate_config'
    migrate_from = '0021_auto_20180220_1049'
    migrate_to = '0023_destroy_repository_plugins_table_and_rename'

    def setUpBeforeMigration(self, apps: Apps):
        Repository = apps.get_model('gitmate_config', 'Repository')
        Installation = apps.get_model('gitmate_config', 'Installation')
        Plugin = apps.get_model('gitmate_config', 'Plugin')

        self.inst = Installation(provider='github', identifier=81451)
        self.inst.save()

        repo = Repository(
            provider='github',
            installation=self.inst,
            full_name=environ['GITHUB_TEST_REPO'])
        repo.save()

        self.plugin_names = []

        testplugin = Plugin('testplugin')
        testplugin.save()

        repo.plugins.add(testplugin)
        repo.save()

    def test_successful_migration(self):
        Repository = self.apps.get_model('gitmate_config', 'Repository')
        repo = Repository.objects.get(provider='github',
                                      full_name=environ['GITHUB_TEST_REPO'])

        # ensure that the new plugins field is a list
        self.assertIsInstance(repo.plugins, list)

        # assert that new plugins field contains `testplugin`
        self.assertEquals(repo.plugins, ['testplugin'])
