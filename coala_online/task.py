import json
import subprocess

from celery.task import task

from coala_online.config import COALA_ONLINE_IMAGE


@task(name='run_coala_online')
def run_coala_online(req):
    """
    Takes in a dict with mode, file_content, bears, url and sections
    as keys, and spawns docker container to run coala-quickstart or
    coala on code as specified.
    """
    req_str = json.dumps(req)

    proc = subprocess.Popen(
        ['docker', 'run', '-i', '--rm',
         COALA_ONLINE_IMAGE,
         'python3', 'run.py', req_str],
        stdout=subprocess.PIPE,
    )

    response = json.loads(proc.stdout.read().decode('utf-8'))

    return response
