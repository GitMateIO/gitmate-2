from gitmate.utils import GitmatePluginConfig
from gitmate.enums import PluginCategory


class GitmateAckConfig(GitmatePluginConfig):
    name = 'plugins.gitmate_ack'
    verbose_name = 'Track manual review state of commits'
    plugin_category = PluginCategory.PULLS
    description = ('Sets a status in the pull request depending on whether or '
                   'not all commits have been acknowledged after a manual code'
                   ' review.<br>Acknowledge/Unacknowledge commits of a pull '
                   'request by mentioning a keyword and the commit hash in a '
                   'comment in the discussion.<br>Example comment:<br><br>'
                   '<tt>"ack ab01cd23"</tt>')
