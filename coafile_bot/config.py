import os
from IGitt.GitHub import GitHubToken

from gitmate.settings import BOT_TOKEN

GITHUB_POLL_DELAY = 10.0
MAX_RETRIES_LIMIT = 3
GITHUB_TOKEN = None

if BOT_TOKEN:
    GITHUB_TOKEN = GitHubToken(token=BOT_TOKEN)
