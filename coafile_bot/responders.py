
from coafile_bot.config import GITHUB_POLL_DELAY, GITHUB_TOKEN
from coafile_bot.task import handle_thread
from coafile_bot.utils import post_comment
from gitmate.settings import BOT_USER

from gitmate_hooks.utils import ResponderRegistrar


@ResponderRegistrar.scheduler(interval=GITHUB_POLL_DELAY)
def coafile_bot():
    """
    Runs the coafile bot.
    """
    if not GITHUB_TOKEN or not BOT_USER:
        return  # Bot Inactive

    from IGitt.GitHub.GitHubNotification import GitHubNotification
    notifications = GitHubNotification(token=GITHUB_TOKEN)
    threads = notifications.get_threads()
    for thread in threads:
        if thread.reason == "mention" and thread.unread:
            thread.mark()
            thread.unsubscribe()

            post_comment(thread,
                         'Greetings! I\'m the coafile bot and I\'m here to get your coafile ready. Sit Tight!')

            handle_thread.delay(thread)
