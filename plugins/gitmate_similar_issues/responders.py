from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest


from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(
    'similar_issues',
    MergeRequestActions.SYNCHRONIZED
)
def gitmate_similar_issues(pr: MergeRequest):
    pr.add_comment('Hello World!')
