from coafile_bot.config import MAX_RETRIES_LIMIT, GITHUB_TOKEN
from gitmate.settings import BOT_USER


def parse_issue_num(url):
    """
    Parses issue number from url

    :param url: Url from which issue number is to be parsed
    :return: Issue number
    """
    num_list = url.split('/')
    return num_list[len(num_list) - 1]


def post_comment(thread, message):
    """
    Post comment on GitHub thread

    :param thread: Thread on which comment is to be post
    :param message: Message to comment.
    """

    num = parse_issue_num(thread.data['subject']['url'])
    from IGitt.GitHub.GitHubIssue import GitHubIssue

    issue = GitHubIssue(token=GITHUB_TOKEN, repository=thread.data['repository']['full_name'], number=num)
    issue.add_comment(body=message)


def create_pr(thread, coafile, retries=MAX_RETRIES_LIMIT):
    """
    Creates GitHub PR with coafile

    :param thread: Thread object where mention to coafile is done
    :param coafile: coafile string
    :param retries: Attempts done to create the PR
    :return: If successful return PullRequest object
    """
    from IGitt.GitHub.GitHubRepository import GitHubRepository

    repo = GitHubRepository(token=GITHUB_TOKEN, repository=thread.data['repository']['full_name'])
    clone = repo.create_fork()

    try:
        clone.create_file(path='.coafile', message='coafile: Add coafile',
                          content=coafile, branch='master')
        head = BOT_USER + ':master'
        pr = repo.create_merge_request(title='Add coafile', base='master',
                                       head=head)
        return pr

    except RuntimeError:
        if retries > 0:
            post_comment(
                thread, "Oops! Looks like there was some problem making the coafile PR! Retrying...")
            clone.delete()
            retries -= 1
            create_pr(thread, coafile, retries)
        else:
            post_comment(
                thread, "Sorry! coafile-bot is unable to make the PR.")
