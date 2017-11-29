import json

from IGitt.Interfaces import Notification

from coafile_bot.utils import create_pull_request
from coafile_bot.utils import post_comment
from coala_online.config import COALA_ONLINE_IMAGE
from gitmate.celery import app as celery
from gitmate.utils import run_in_container
from gitmate_hooks.utils import ExceptionLoggerTask


@celery.task(base=ExceptionLoggerTask, ignore_result=True)
def handle_notification(notification: Notification, username: str):
    """
    Handler for notifications.

    :param notification: The notification where the bot was mentioned.
    """
    subject, repo = notification.subject, notification.repository
    req = {'mode': 'bears', 'url': repo.clone_url}
    response = json.loads(run_in_container(COALA_ONLINE_IMAGE,
                                           'python3', 'run.py',
                                           json.dumps(req)))
    coafile = response['coafile']
    post_comment(subject,
                 'Here\'s your coafile: :tada:\n\n```{}```'.format(coafile))
    pull_request = create_pull_request(repo, username, subject, coafile)
    if pull_request:
        message = (
            'Successfully created the coafile pull request! :tada: \n\n\n'
            'Further Steps: \n\n'
            '- Merge the Pull Request {pr_url} with the .coafile\n'
            '- Turn on [GitMate](https://gitmate.io) Integration '
            'for this repository.\n'
            '- Turn on code analysis for automated code reviews on all '
            'your pull requests.\n\n'
            'Happy Linting! :tada:').format(pr_url=pull_request.web_url)
        post_comment(subject, message)
