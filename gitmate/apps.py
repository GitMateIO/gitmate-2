from typing import List

from django.apps import apps

from gitmate.utils import GitmatePluginConfig


def get_all_plugins(
        default_only=False, repo=None
) -> List[GitmatePluginConfig]:
    """
    Returns the list of configurations for all GitMate plugins.

    :param default_only:
        If ``default_only`` is set to ``True``, only the plugins which were
        configured to be enabled upon repo activation will be returned.
    :param repo:
        If ``repo`` parameter is provided, then only the active plugins on that
        repository will be returned.
    """
    return [config for config in apps.get_app_configs()
            if config.name.startswith('plugins.gitmate_') and
            (config.enable_on_repo_activation if default_only else True) and
            (config.plugin_name in repo.plugins if repo else True) and
            config.importable]
