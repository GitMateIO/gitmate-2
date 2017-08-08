import re

from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.CommitStatus import Status, CommitStatus
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Comment import Comment

from gitmate_config.models import Repository
from gitmate_hooks import ResponderRegistrar

from plugins.gitmate_ack.models import MergeRequestModel


def get_keywords(string: str):
    return tuple(elem.strip().lower()
                 for elem in string.split(',') if elem.strip())


def unack(commit):
    commit.set_status(CommitStatus(
        Status.FAILED, 'This commit needs work.',
        'review/gitmate/manual', 'https://gitmate.io/'))


def ack(commit):
    commit.set_status(CommitStatus(
        Status.SUCCESS, 'This commit was acknowledged.',
        'review/gitmate/manual', 'https://gitmate.io/'))


def pending(commit):
    for status in commit.get_statuses():
        if status.context == 'review/gitmate/manual':
            return {
                Status.FAILED: False,
                Status.ERROR: False,
                Status.CANCELED: False,
                Status.SUCCESS: True,
            }.get(status.status)

    commit.set_status(CommitStatus(
        Status.PENDING, 'This commit needs review.',
        'review/gitmate/manual', 'https://gitmate.io'))

    return None


@ResponderRegistrar.responder(
    'ack',
    MergeRequestActions.COMMENTED
)
def gitmate_ack(pr: MergeRequest,
                comment: Comment,
                ack_strs: str = 'ack, reack',
                unack_strs: str = 'unack'):
    """
    A responder to ack and unack commits
    """
    body = comment.body.lower()
    commits = pr.commits
    pattern = '(^{k}\s)|(\s{k}\s)|(\s{k}$)'

    db_pr = MergeRequestModel.objects.filter(
        repository=Repository.from_igitt_repo(pr.repository),
        number=pr.number,
    )

    unack_strs = get_keywords(unack_strs)
    for kw in unack_strs:
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    commit.unack()
                    db_pr.acks[commit.sha] = False

    ack_strs = get_keywords(ack_strs)
    for kw in ack_strs:
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    commit.ack()
                    db_pr.acks[commit.sha] = True

    pr.head.set_status(db_pr.ack_state)


@ResponderRegistrar.responder(
        'ack',
        MergeRequestActions.OPENED,
        MergeRequestActions.SYNCHRONIZED)
def add_review_pending_status(pr: MergeRequest):
    """
    A responder to add pending status on commits on
    MergeRequest SYNCHRONIZED and OPENED event.
    """
    db_pr = MergeRequestModel.objects.filter(
        repository=Repository.from_igitt_repo(pr.repository),
        number=pr.number,
    )

    commits = pr.commits
    for commit in commits:
        db_pr.acks[commit.sha] = commit.pending()

    pr.head.set_status(db_pr.ack_state)
