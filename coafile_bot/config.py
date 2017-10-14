from django.conf import settings
from IGitt.GitHub import GitHubToken
from IGitt.GitHub.GitHubUser import GitHubUser
from IGitt.GitHub.GitHubNotification import GitHubNotification
from IGitt.GitLab import GitLabPrivateToken
from IGitt.GitLab.GitLabUser import GitLabUser
from IGitt.GitLab.GitLabNotification import GitLabNotification


POLL_DELAY = '*/10 * * * *'
HOSTER_CONFIG = []

try:
    token = GitHubToken(settings.GITHUB_BOT_TOKEN)
    HOSTER_CONFIG.append({
        'token': token,
        'username': GitHubUser(token).username,
        'cls': GitHubNotification
    })
except BaseException:
    pass

try:
    token = GitLabPrivateToken(settings.GITLAB_BOT_TOKEN)
    HOSTER_CONFIG.append({
        'token': token,
        'username': GitLabUser(token).username,
        'cls': GitLabNotification
    })
except BaseException:
    pass
