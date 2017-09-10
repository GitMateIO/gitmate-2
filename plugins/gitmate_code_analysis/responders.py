from os import environ
import json
import logging
import shlex
import subprocess
from traceback import print_exc

from IGitt.GitHub.GitHubMergeRequest import GitHubMergeRequest
from IGitt.GitLab.GitLabMergeRequest import GitLabMergeRequest
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Commit import Commit
from IGitt.Interfaces.Commit import CommitStatus
from IGitt.Interfaces.Commit import Status
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate_config.models import Repository
from gitmate_hooks import ResponderRegistrar
from .models import AnalysisResults


# timeout for docker container in seconds, setting upto 10 minutes
CONTAINER_TIMEOUT = 60 * 10


def _set_status(commit: Commit, status: Status, context: str):
    pr_or_commit = 'PR' if 'pr' in context else 'commit'
    commit_status = CommitStatus(status, {
        Status.RUNNING: 'GitMate-2 analysis in progress...',
        Status.FAILED: 'This {} has issues!'.format(pr_or_commit),
        Status.SUCCESS: 'This {} has no issues. :)'.format(pr_or_commit),
        Status.ERROR: 'Oops.. GitMate broke down. :('
    }.get(status), context, 'http://gitmate.io')
    commit.set_status(commit_status)


def analyse(repo, sha, clone_url, ref, coafile_location):
    """
    Spawns a docker container to run code analysis on a specified directory.

    This will auto store results in the db and fetch them instead of doing
    the anlaysis if it's there.
    """
    coafile_location = shlex.quote(
        coafile_location.replace('..', '').lstrip('/')
    )

    try:
        # Cached result available
        return AnalysisResults.objects.get(
            repo=repo, sha=sha, coafile_location=coafile_location).results
    except AnalysisResults.DoesNotExist:
        proc = subprocess.Popen(
            ['docker', 'run', '-i', '--rm',
             environ['COALA_RESULTS_IMAGE'],
             'python3', 'run.py', sha, clone_url, ref, coafile_location],
            stdout=subprocess.PIPE,
        )
        output = proc.stdout.read().decode('utf-8')
        try:
            results = json.loads(output)
        except json.JSONDecodeError:  # pragma: no cover, for debugging
            logging.error('coala image output was not JSON parsable. Output '
                          'was: ' + output)
            raise

        proc.wait()

        AnalysisResults.objects.create(repo=repo, sha=sha, results=results,
                                       coafile_location=coafile_location)
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
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
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
        patch += ('\n\n```diff\n' +
                  diff.replace('--- \n+++ \n',
                               '--- a/' + filename + '\n'
                               '+++ b/' + filename + '\n') +
                  '```')
    return ('\n\nThe issue can be fixed by applying the following patch:' +
            patch)


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


def get_ref(pr):  # pragma: no cover, testing this with mocks is meaningless
    if isinstance(pr, GitHubMergeRequest):
        return 'refs/pull/{}/head'.format(pr.number)

    if isinstance(pr, GitLabMergeRequest):
        return 'merge-requests/{}/head'.format(pr.number)

    raise NotImplementedError


@ResponderRegistrar.responder(
    'code_analysis',
    MergeRequestActions.SYNCHRONIZED,
    MergeRequestActions.OPENED
)
def run_code_analysis(pr: MergeRequest, pr_based_analysis: bool=True,
                      coafile_location: str='.coafile'):
    """
    Starts code analysis on the merge request.
    """
    # Use constant list of commits for this analysis:
    # The PR might change while the analysis is in progress
    COMMITS = set(pr.commits)
    HEAD = pr.head
    ANALYZED_COMMITS = set()

    igitt_repo = pr.repository
    repo = Repository.objects.filter(
        active=True,
        full_name=igitt_repo.full_name).first()

    # set status as review in progress
    if pr_based_analysis is False:
        for commit in COMMITS:
            _set_status(commit, Status.RUNNING, 'review/gitmate/commit')

    _set_status(HEAD, Status.RUNNING, 'review/gitmate/pr')

    ref = get_ref(pr)
    status = Status.SUCCESS

    try:
        # Spawn a coala container for base commit to generate old results.
        old_results = analyse(
            repo, pr.base.sha, igitt_repo.clone_url, ref, coafile_location)

        # Run coala only on head.
        if pr_based_analysis is True:
            new_results = analyse(
                repo, HEAD.sha, igitt_repo.clone_url, ref, coafile_location)

            filtered_results = filter_results(old_results, new_results)
            add_comment(HEAD, filtered_results, mr_num=pr.number)

            # set pr status as failed if any results are found
            if any(s_results for _, s_results in filtered_results.items()):
                status = Status.FAILED

        else:  # Run coala per commit
            for commit in COMMITS:
                new_results = analyse(
                    repo, commit.sha, igitt_repo.clone_url,
                    ref, coafile_location)

                filtered_results = filter_results(old_results, new_results)
                old_results = new_results

                add_comment(commit, filtered_results, mr_num=pr.number)

                # set commit status as failed if any results are found
                if any(s_results for _, s_results in filtered_results.items()):
                    status = Status.FAILED

                _set_status(commit, status, 'review/gitmate/commit')
                ANALYZED_COMMITS.add(commit)

        _set_status(pr.head, status, 'review/gitmate/pr')

    except BaseException as exc:  # pragma: no cover
        # Attempt to set ``Status.ERROR`` for all commits that were not
        # analyzed when a new push event occured. However, if these commits
        # continue to be a part of this merge request, the new task would
        # process it properly.
        if pr_based_analysis is False:
            for commit in COMMITS - ANALYZED_COMMITS:
                try:
                    _set_status(commit, Status.ERROR, 'review/gitmate/commit')
                except RuntimeError:
                    pass

        try:
            _set_status(HEAD, Status.ERROR, 'review/gitmate/pr')
        except RuntimeError:
            pass
        print(str(exc))
        print_exc()
