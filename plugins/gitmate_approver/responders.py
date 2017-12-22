from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Actions import PipelineActions
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.CommitStatus import Status
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate_config.models import Repository
from gitmate_hooks.utils import ResponderRegistrar

from .models import MergeRequestModel


@ResponderRegistrar.responder(
    'approver',
    MergeRequestActions.OPENED,
    MergeRequestActions.SYNCHRONIZED,
)
def store_head_commit_sha(pr: MergeRequest):
    """
    Stores the list of merge requests along with their heads and updates it on
    synchronizing again.
    """
    MergeRequestModel.objects.update_or_create(
        repo=Repository.from_igitt_repo(pr.repository),
        number=pr.number,
        defaults={'head_sha': pr.head.sha})


@ResponderRegistrar.responder(
    'approver', PipelineActions.UPDATED)
def add_approved_label(
        commit: Commit,
        approved_label: str='status/approved',
        status_labels: str='status/pending_review, status/WIP'
):
    """
    Labels the PR as approved when the head commit passes all tests.
    """
    status_labels = [label.strip() for label in status_labels.split(',')
                     if label.strip()]
    try:
        pr = MergeRequestModel.objects.get(head_sha=commit.sha).igitt_pr
        with lock_igitt_object('label mr', pr):
            labels = pr.labels
            if commit.combined_status is Status.SUCCESS:
                pr.labels = {approved_label} | labels - set(status_labels)
            else:
                pr.labels = labels - {approved_label}
    except MergeRequestModel.DoesNotExist:  # pragma: no cover
        # Merge request containing this commit hasn't been opened yet
        pass
