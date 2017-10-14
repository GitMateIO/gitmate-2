import json

from django_rq import job

from coala_online.config import COALA_ONLINE_IMAGE
from gitmate.utils import run_in_container


@job
def run_coala_online(req):
    """
    Takes in a dict with mode, file_content, bears, url and sections
    as keys, and spawns docker container to run coala-quickstart or
    coala on code as specified.
    """
    return json.loads(run_in_container(COALA_ONLINE_IMAGE,
                                       'python3', 'run.py', json.dumps(req)))
