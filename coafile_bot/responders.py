from IGitt.Interfaces import Token
from IGitt.Interfaces.Notification import Reason

from coafile_bot.config import POLL_DELAY
from coafile_bot.config import HOSTER_CONFIG
from coafile_bot.task import handle_notification
from coafile_bot.utils import post_comment
from gitmate_hooks import ResponderRegistrar


def run_coafile_bot(token: Token, cls: type, username: str):
    """
    Runs the coafile bot.

    :param token:       The OAuth token.
    :param cls:         The class for instantiating Notification objects.
    :param username:    The name of the coafile bot user.
    """
    for notification in cls.fetch_all(token):
        if notification.reason == Reason.MENTIONED and notification.pending:
            notification.mark_done()
            notification.unsubscribe()
            post_comment(notification.subject,
                         'Greetings! I am the coafile bot. Sit Tight! '
                         'I will get your coafile ready.')
            handle_notification.delay(notification, username)


@ResponderRegistrar.scheduler(interval=POLL_DELAY)
def poll_for_mentions():
    """
    Checks the notifications for mentions.
    """
    for config in HOSTER_CONFIG:
        run_coafile_bot(**config)
