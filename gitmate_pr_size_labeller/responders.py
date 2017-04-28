from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(
    'pr_size_labeller',
    MergeRequestActions.SYNCHRONIZED,
)
def add_labels_based_on_size(pr: MergeRequest):
    """
    Labels the pull request with size labels according to the amount of
    code touched, commits and files involved. Helps plan the review in
    advance.
    """
    labels = pr.issue.labels.difference({
        'size/XXL', 'size/XL', 'size/L', 'size/M', 'size/S', 'size/XS'
    })

    lines_added, lines_deleted = pr.diffstat
    commit_score = 4 * len(pr.commits)
    file_score = 4 * len(pr.affected_files)

    if commit_score + file_score + lines_added + lines_deleted <= 100:
        pr.issue.labels = {'size/XS'}.union(labels)

    elif commit_score + file_score + lines_added + lines_deleted <= 250:
        pr.issue.labels = {'size/S'}.union(labels)

    elif commit_score + file_score + lines_added + lines_deleted <= 500:
        pr.issue.labels = {'size/M'}.union(labels)

    elif commit_score + file_score + lines_added + lines_deleted <= 1000:
        pr.issue.labels = {'size/L'}.union(labels)

    elif commit_score + file_score + lines_added + lines_deleted <= 1500:
        pr.issue.labels = {'size/XL'}.union(labels)

    else:
        pr.issue.labels = {'size/XXL'}.union(labels)
