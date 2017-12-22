import shutil

import bugspots3
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import lock_igitt_object
from gitmate_hooks.utils import ResponderRegistrar


def get_hotspot_files(pattern: str, pr: MergeRequest):
    """
    Retrieves the hotspot files for the given repository.
    """
    _, path = pr.repository.get_clone()
    try:
        b = bugspots3.Bugspots(grep=pattern, path=path)
        return {hotspot.filename for hotspot in b.get_hotspots()}
    finally:
        shutil.rmtree(path)


@ResponderRegistrar.responder(
    'bug_spotter',
    MergeRequestActions.SYNCHRONIZED,
    MergeRequestActions.OPENED
)
def label_hotspots(
    pr: MergeRequest,
    pattern: str = 'Pattern for matching against',
    hotspot_label: str = 'Label to be added if hotspot found',
):
    if len(get_hotspot_files(pattern, pr).intersection(pr.affected_files)):
        with lock_igitt_object('label mr', pr):
            pr.labels |= {hotspot_label}
