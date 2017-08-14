from hashlib import sha1

from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.CommitStatus import CommitStatus, Status
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate_hooks import ResponderRegistrar


def get_commit_hash(commit: Commit):
    """
    Generates a unique hash from the commit message and unified diff.
    """
    return sha1((commit.message + commit.unified_diff).encode()).hexdigest()


@ResponderRegistrar.responder(
    'reack', MergeRequestActions.SYNCHRONIZED, MergeRequestActions.OPENED)
def reacknowledge_commits(pr: MergeRequest):
    """
    Reacknowledges the commits on a freshly resynchronized pull request based
    on the status from their earlier state.
    """
    from gitmate_config.models import Repository
    from .models import CommitModel

    for commit in pr.commits:
        commit_object, created = CommitModel.objects.get_or_create(
            repo=Repository.from_igitt_repo(pr.repository),
            hash_value=get_commit_hash(commit),
            defaults={'status': commit.combined_status})
        if created is False:
            with lock_igitt_object('status commit', commit):
                commit.set_status(
                    CommitStatus(Status(commit_object.status)),
                    'Copied earlier status..', 'reack/gitmate/pr')
