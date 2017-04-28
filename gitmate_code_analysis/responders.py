from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_hooks import ResponderRegistrar


@ResponderRegistrar.responder(
    'code_analysis',
    MergeRequestActions.SYNCHRONIZED
)
def run_code_analysis(pr: MergeRequest):
    pr.issue.add_comment('Im analyzing it now. (Ok no. This is just a mock.)')
