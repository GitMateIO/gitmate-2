import re

from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.CommitStatus import Status, CommitStatus
from IGitt.Interfaces.MergeRequest import MergeRequest
from IGitt.Interfaces.Comment import Comment

from gitmate_hooks import ResponderRegistrar


def get_keywords(string: str):
    return tuple(elem.strip().lower()
                 for elem in string.split(',') if elem.strip())


def unack(commit):
    commit.set_status(CommitStatus(
        Status.FAILED, 'This commit needs work.',
        'review/gitmate/manual', 'https://gitmate.io/'))
    return False


def ack(commit):
    commit.set_status(CommitStatus(
        Status.SUCCESS, 'This commit was acknowledged.',
        'review/gitmate/manual', 'https://gitmate.io/'))
    return True


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
    # Don't move to module code! Apps aren't loaded yet.
    from gitmate_config.models import Repository
    from .models import MergeRequestModel

    body = comment.body.lower()
    commits = pr.commits
    pattern = r'(^{k}\s)|(\s{k}\s)|(\s{k}$)'

    db_pr = MergeRequestModel.objects.get(
        repo=Repository.from_igitt_repo(pr.repository),
        number=pr.number)

    unack_strs = get_keywords(unack_strs)
    for kw in unack_strs:
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    db_pr.acks[commit.sha] = unack(commit)

    ack_strs = get_keywords(ack_strs)
    for kw in ack_strs:
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    db_pr.acks[commit.sha] = ack(commit)

    db_pr.save()
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
    # Don't move to module code! Apps aren't loaded yet.
    from gitmate_config.models import Repository
    from .models import MergeRequestModel

    db_pr, _ = MergeRequestModel.objects.get_or_create(
        repo=Repository.from_igitt_repo(pr.repository),
        number=pr.number)

    for commit in pr.commits:
        db_pr.acks[commit.sha] = pending(commit)

    db_pr.save()
    pr.head.set_status(db_pr.ack_state)
