from social_core.backends.github import GithubOAuth2


class GitHubAppOAuth2(GithubOAuth2):
    """
    Social Authentication backend for GitHub App User OAuth2.
    """
    name = 'github-app'
    REDIRECT_STATE = False
