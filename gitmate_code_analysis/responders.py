import json
import logging
from os import environ
import subprocess
from subprocess import PIPE
from traceback import print_exc

from gitmate_hooks import ResponderRegistrar
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.Commit import CommitStatus
from IGitt.Interfaces.Commit import Status
from IGitt.Interfaces.MergeRequest import MergeRequest

# timeout for docker container in seconds, setting upto 10 minutes
CONTAINER_TIMEOUT = 60 * 10


def analyse(repo, sha, clone_url, ref):
    """
    Spawns a docker container to run code analysis on a specified directory.

    This will auto store results in the db and fetch them instead of doing
    the anlaysis if it's there.
    """
    # Don't move to module code! Apps aren't loaded yet.
    from gitmate_code_analysis.models import AnalysisResults

    try:
        # Cached result available
        return AnalysisResults.objects.get(
            repo=repo, sha=sha).results
    except AnalysisResults.DoesNotExist:
        proc = subprocess.Popen(
            ['docker', 'run', '-i', '--rm',
             environ['COALA_RESULTS_IMAGE'],
             'python3', 'run.py', sha, clone_url, ref],
            stdout=PIPE,
        )
        output = proc.stdout.read().decode('utf-8')
        try:
            results = json.loads(output)
        except json.JSONDecodeError:  # pragma: no cover, for debugging
            logging.error('coala image output was not JSON parsable. Output '
                          'was: ' + output)
            raise

        proc.wait()

        AnalysisResults.objects.create(repo=repo, sha=sha, results=results)
        return results


def filter_results(old_results: dict, new_results: dict):
    """
    Spawns a docker container to run result bouncer that spits out only the
    required results.
    """
    results = {
        'old_files': old_results['file_dicts'],
        'new_files': new_results['file_dicts'],
        'old_results': old_results['results'],
        'new_results': new_results['results']
    }

    proc = subprocess.Popen(
        ['docker', 'run', '-i', '--rm',
         environ['RESULTS_BOUNCER_IMAGE'],
         'python3', 'bouncer.py'],
        stdin=PIPE,
        stdout=PIPE,
    )
    proc.stdin.write(json.dumps(results).encode('utf-8'))
    proc.stdin.close()
    filtered_results = json.loads(proc.stdout.read().decode('utf-8'))
    proc.wait()

    return filtered_results


def describe_patch(diffs):
    patch = ''
    for filename, diff in diffs.items():
        filename = filename.lstrip('/')
        patch += '\n\n```diff\n'+diff.replace(
                '--- \n+++ \n',
                '--- a/'+filename+'\n+++ b/'+filename+'\n'
        ) + '```'
    return '\n\nThe issue can be fixed by applying the following patch:'+patch


def get_file_and_line(result):
    if result.get('affected_code'):
        start_dict = result['affected_code'][0]['start']
        file = start_dict['file'].lstrip('/')
        line = start_dict['line']
    else:
        file = None
        line = None

    return file, line


def result_table_row(result):
    file, line = get_file_and_line(result)
    return '| {} | {} | {} |'.format(
        result.get('message').replace('\n', ' '), str(file), str(line)
    )


def add_comment(commit: Commit, results: dict, mr_num: int=None):
    for section_name, section_results in results.items():
        if len(section_results) > 10:
            commit.comment(
                'There are {} results for the section {}. They have been '
                'shortened and will not be shown inline because they are more '
                'than 10.\n\n'
                '| Message | File | Line |\n'
                '|---|---|---|\n{}\n\n'
                'Until GitMate provides an online UI to show a better '
                'overview, you can run [coala](https://coala.io/) locally for '
                'more details.'
                .format(
                    len(section_results),
                    section_name,
                    '\n'.join(result_table_row(result)
                              for result in section_results)
                )
            )
            continue
        for result in section_results:
            file, line = get_file_and_line(result)
            patch = describe_patch(result['diffs']) if result['diffs'] else ''

            commit.comment(
                ('{message}\n'
                 '\n'
                 '*Origin: {origin}, Section: `{section}`.*{patch}')
                .format(message=result.get('message'),
                        origin=result.get('origin'),
                        section=section_name,
                        patch=patch),
                file, line, mr_number=mr_num)


@ResponderRegistrar.responder(
    'code_analysis',
    MergeRequestActions.SYNCHRONIZED
)
def run_code_analysis(pr: MergeRequest, pr_based_analysis: bool=True):
    """
    Starts code analysis on the merge request.
    """
    # Don't move to module code! Apps aren't loaded yet.
    from gitmate_config.models import Repository

    igitt_repo = pr.repository
    repo = Repository.objects.filter(
        active=True,
        full_name=igitt_repo.full_name).first()

    # set status as review in progress
    if pr_based_analysis is False:
        for commit in pr.commits:
            commit.set_status(CommitStatus(
                Status.PENDING, 'GitMate-2 analysis in progress...',
                'GitMate-2 Commit Review', 'http://2.gitmate.io'))
    else:
        pr.head.set_status(CommitStatus(
            Status.PENDING, 'GitMate-2 analysis in progress...',
            'GitMate-2 PR Review', 'http://2.gitmate.io/'))

    # This is github specific, to be fixed
    ref = 'refs/pull/{}/head'.format(pr.number)
    try:
        # Spawn a coala container for base commit to generate old results.
        old_results = analyse(repo, pr.base.sha, igitt_repo.clone_url, ref)

        # Run coala only on head.
        if pr_based_analysis is True:
            new_results = analyse(repo, pr.head.sha, igitt_repo.clone_url, ref)

            filtered_results = filter_results(old_results, new_results)
            add_comment(pr.head, filtered_results, mr_num=pr.number)

            # set pr status as failed if any results are found
            if any(s_results for _, s_results in filtered_results.items()):
                pr.head.set_status(CommitStatus(
                    Status.FAILED, 'This PR has issues!',
                    'GitMate-2 PR Review', 'http://2.gitmate.io/'))
            else:
                pr.head.set_status(CommitStatus(
                    Status.SUCCESS, 'This PR has no issues. :)',
                    'GitMate-2 PR Review', 'http://2.gitmate.io/'))
        else:  # Run coala per commit
            for commit in pr.commits:
                new_results = analyse(
                    repo, commit.sha, igitt_repo.clone_url, ref)

                filtered_results = filter_results(old_results, new_results)
                old_results = new_results

                add_comment(commit, filtered_results, mr_num=pr.number)

                # set commit status as failed if any results are found
                if any(s_results for _, s_results in filtered_results.items()):
                    commit.set_status(CommitStatus(
                        Status.FAILED, 'This commit has issues!',
                        'GitMate-2 Commit Review', 'http://2.gitmate.io/'))
                else:
                    commit.set_status(CommitStatus(
                        Status.SUCCESS, 'This commit has no issues. :)',
                        'GitMate-2 Commit Review', 'http://2.gitmate.io/'))
    except Exception as exc:  # pragma: no cover
        print(str(exc))
        print_exc()
