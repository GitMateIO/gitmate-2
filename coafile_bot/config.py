import logging
from django.conf import settings
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitLab import GitLabPrivateToken
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.GitLab.GitLabNotification import GitLabNotification


POLL_DELAY = 10.0
HOSTER_CONFIG = []

try:
    if settings.GITHUB_BOT_TOKEN:
        token = GitHubToken(settings.GITHUB_BOT_TOKEN)
        HOSTER_CONFIG.append({
            'token': token,
            'username': GitHubUser(token).username,
            'cls': GitHubNotification
        })
except RuntimeError:
    logging.warning(f'coafile bot GitHub token {settings.GITHUB_BOT_TOKEN} '
                    f'is invalid.')

try:
    if settings.GITLAB_BOT_TOKEN:
        token = GitLabPrivateToken(settings.GITLAB_BOT_TOKEN)
        HOSTER_CONFIG.append({
            'token': token,
            'username': GitLabUser(token).username,
            'cls': GitLabNotification
        })
except RuntimeError:
    logging.warning(f'coafile bot GitLab token {settings.GITLAB_BOT_TOKEN} '
                    f'is invalid.')

logging.info(f'Got coafile bot tokens: {HOSTER_CONFIG}')
