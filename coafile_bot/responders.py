
from coafile_bot.config import BOT_TOKEN, GITHUB_POLL_DELAY
from coafile_bot.task import handle_thread
from coafile_bot.utils import post_comment

from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.scheduler(interval=GITHUB_POLL_DELAY)
def coafile_bot():
    from IGitt.GitHub.GitHubNotification import GitHubNotification
    notifications = GitHubNotification(token=BOT_TOKEN)
    threads = notifications.get_threads()
    for thread in threads:
        if thread.reason == "mention" and thread.unread:
            thread.mark()
            thread.unsubscribe()

            post_comment(thread,
                         'Greetings! I\'m the coafile bot and I\'m here to get your coafile ready. Sit Tight!')

            handle_thread.delay(thread)
