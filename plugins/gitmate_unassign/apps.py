
from gitmate.utils import GitmatePluginConfig
from gitmate.utils import PluginCategory


class GitmateUnassignConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_unassign'
    verbose_name = '' # Add something verbose here
    plugin_category = PluginCategory.PULLS # Add plugin category here
    # Valid plugin categories are PULLS, ISSUE and ANALYSIS
    description = '' # Add description here
