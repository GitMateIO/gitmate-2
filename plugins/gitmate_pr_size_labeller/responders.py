from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(
    'pr_size_labeller',
    MergeRequestActions.SYNCHRONIZED,
    MergeRequestActions.OPENED,
)
def add_labels_based_on_size(pr: MergeRequest, size_scheme: str='size/{size}'):
    """
    Labels the pull request with size labels according to the amount of
    code touched, commits and files involved. Helps plan the review in
    advance.
    """
    sizes = {'XXL', 'XL', 'L', 'M', 'S', 'XS'}
    with lock_igitt_object('label mr', pr):
        labels = pr.labels.difference({
            size_scheme.format(size=size) for size in sizes
        })

        lines_added, lines_deleted = pr.diffstat
        commit_score = 4 * len(pr.commits)
        file_score = 4 * len(pr.affected_files)

        if commit_score + file_score + lines_added + lines_deleted <= 100:
            pr.labels = {size_scheme.format(size='XS')}.union(labels)

        elif commit_score + file_score + lines_added + lines_deleted <= 250:
            pr.labels = {size_scheme.format(size='S')}.union(labels)

        elif commit_score + file_score + lines_added + lines_deleted <= 500:
            pr.labels = {size_scheme.format(size='M')}.union(labels)

        elif commit_score + file_score + lines_added + lines_deleted <= 1000:
            pr.labels = {size_scheme.format(size='L')}.union(labels)

        elif commit_score + file_score + lines_added + lines_deleted <= 1500:
            pr.labels = {size_scheme.format(size='XL')}.union(labels)

        else:
            pr.labels = {size_scheme.format(size='XXL')}.union(labels)
