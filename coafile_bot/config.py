import os
from IGitt.GitHub import GitHubToken


GITHUB_POLL_DELAY = 10.0
MAX_RETRIES_LIMIT = 3
BOT_TOKEN= GitHubToken(os.environ['COAFILE_BOT_GITHUB_TOKEN'])
