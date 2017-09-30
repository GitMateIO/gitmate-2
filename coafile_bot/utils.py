from typing import Union
from typing import Optional

from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.Issue import Issue
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Repository import Repository


def post_comment(subject: Union[Commit, Issue, MergeRequest], message: str):
    """
    Helper function to add comment based on the type of subject.
    """
    if isinstance(subject, Commit):
        subject.comment(message)
    elif issubclass(subject, Issue):
        subject.add_comment(message)


def create_pr(repo: Repository,
              username: str,
              subject: Union[Commit, Issue, MergeRequest],
              coafile: str) -> Optional[MergeRequest]:
    """
    Creates a new merge request with coafile.

    :param repo:        The repository where the bot is mentioned.
    :param username:    The username of the coafile bot.
    :param subject:     The subject (Commit/MergeRequest/Issue) where the bot
                        was mentioned.
    :param coafile:     The content of coafile.
    :return:            If successful, returns the MergeRequest else None.
    """
    try:
        clone = repo.create_fork()
        clone.create_file(path='.coafile', message='coafile: Add coafile',
                          content=coafile, branch='master')
        return repo.create_merge_request(title='Add coafile', base='master',
                                         head=username + ':master')
    except RuntimeError:
        post_comment(subject,
                     'Sorry! {} is unable to make the PR.'.format(username))
