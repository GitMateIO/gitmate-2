from hashlib import sha1
import re

from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.CommitStatus import CommitStatus
from IGitt.Interfaces.CommitStatus import Status
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_config.models import Repository
from gitmate_hooks.utils import ResponderRegistrar
from .models import MergeRequestModel


def _get_commit_hash(commit: Commit):
    """
    Returns a unique hash generated from the commit message and unified diff
    discarding line numbers.
    """
    diff = '\n'.join([line for line in commit.unified_diff.split('\n')
                      if not line.startswith('@@')])
    return sha1((commit.message + diff).encode()).hexdigest()


def _status_to_dict(state: CommitStatus):
    return {
        'status': state.status.value,
        'description': state.description,
        'context': state.context,
        'url': state.url
    }


def _dict_to_status(state: dict):
    return CommitStatus(**{**state, 'status': Status(state['status'])})


def get_keywords(string: str):
    return tuple(elem.strip().lower()
                 for elem in string.split(',') if elem.strip())


def unack(commit: Commit):
    state = CommitStatus(Status.FAILED, 'This commit needs work. :(',
                         'review/gitmate/manual', 'https://gitmate.io')
    commit.set_status(state)
    return state


def ack(commit: Commit):
    state = CommitStatus(Status.SUCCESS, 'This commit was acknowledged. :)',
                         'review/gitmate/manual', 'https://gitmate.io')
    commit.set_status(state)
    return state


def pending(commit: Commit):
    for status in commit.get_statuses():
        if status.context == 'review/gitmate/manual':
            return status

    state = CommitStatus(Status.PENDING, 'This commit needs review.',
                         'review/gitmate/manual', 'https://gitmate.io')
    commit.set_status(state)
    return state


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
    pattern = r'(^{k}\s)|(\s{k}\s)|(\s{k}$)'

    db_pr = MergeRequestModel.objects.get(
        repo=Repository.from_igitt_repo(pr.repository),
        number=pr.number)

    for kw in get_keywords(unack_strs):
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    db_pr.acks[_get_commit_hash(commit)] = _status_to_dict(
                        unack(commit))

    for kw in get_keywords(ack_strs):
        if re.search(pattern.format(k=kw), body):
            for commit in commits:
                if commit.sha[:6] in body:
                    db_pr.acks[_get_commit_hash(commit)] = _status_to_dict(
                        ack(commit))

    db_pr.save()
    pr.head.set_status(db_pr.ack_state)


@ResponderRegistrar.responder(
    'ack',
    MergeRequestActions.OPENED,
    MergeRequestActions.SYNCHRONIZED
)
def add_review_status(pr: MergeRequest):
    """
    A responder to add pending/acknowledged/rejected status on commits on
    MergeRequest SYNCHRONIZED and OPENED events based on their generated
    commit hashes (generated from the unified diff and commit message).
    """
    db_pr, _ = MergeRequestModel.objects.get_or_create(
        repo=Repository.from_igitt_repo(pr.repository),
        number=pr.number,
        defaults={'acks': dict()})  # TODO: works only if set manually

    head = pr.head

    hashes = []
    for commit in pr.commits:
        commit_hash = _get_commit_hash(commit)
        hashes.append(commit_hash)

        # This commit was head of the PR before, deletion of the PR state is not
        # possible so we make it green to clean it up.
        if commit.sha == db_pr.last_head != head.sha:
            commit.set_status(CommitStatus(
                Status.SUCCESS, 'Outdated. Check ' + head.sha[:7] + ' instead.',
                'review/gitmate/manual/pr', 'https://gitmate.io'))

        # copying status from unmodified commits in the same merge request
        if commit_hash in db_pr.acks:
            commit.set_status(_dict_to_status(db_pr.acks[commit_hash]))
        else:
            db_pr.acks[commit_hash] = _status_to_dict(pending(commit))

    for chash in dict(db_pr.acks).keys():
        if not chash in hashes:
            del db_pr.acks[chash]

    db_pr.last_head = head.sha
    db_pr.save()
    pr.head.set_status(db_pr.ack_state)
