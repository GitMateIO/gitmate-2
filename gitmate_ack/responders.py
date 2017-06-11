import re

from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Comment import Comment

from gitmate_hooks import ResponderRegistrar


def get_keywords(string: str):
    return tuple(elem.strip().lower()
                 for elem in string.split(',') if elem.strip())


@ResponderRegistrar.responder(
    'ack',
    MergeRequestActions.COMMENTED
)
def gitmate_ack(pr: MergeRequest,
                comment: Comment,
                ack_strs: str = 'ack',
                unack_strs: str = 'unack'):
    """
    A responder to ack and unack commits
    """
    body = comment.body.lower()
    commits = pr.commits
    pattern = '(^{k}\s)|(\s{k}\s)|(\s{k}$)'

    unack_strs = get_keywords(unack_strs)
    for kw in unack_strs:
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    commit.unack()

    ack_strs = get_keywords(ack_strs)
    for kw in ack_strs:
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    commit.ack()
