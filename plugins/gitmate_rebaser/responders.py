import json
import re

from django.conf import settings
from IGitt.Interfaces import AccessLevel
from IGitt.Interfaces.Actions import MergeRequestActions
from IGitt.Interfaces.Comment import Comment
from IGitt.Interfaces.MergeRequest import MergeRequest

from gitmate.utils import run_in_container
from gitmate_config.models import Repository
from gitmate_hooks.utils import ResponderRegistrar


COMMAND_REGEX = r'@(?:{}|gitmate-bot)\s+((?:rebase|merge|fastforward|ff))'


def verify_command_access(comment: Comment, cmd: str):
    """
    Verifies if the author of comment has access to perform the operation.
    """
    perm_levels = {
        'rebase': AccessLevel.CAN_READ,
        'merge': AccessLevel.ADMIN,
        'fastforward': AccessLevel.ADMIN
    }
    author_perm = comment.repository.get_permission_level(comment.author)
    if author_perm.value >= perm_levels[cmd].value:
        return True
    return False


def get_matched_command(body: str, username: str):
    """
    Retrieves the matching command from the comment body.
    """
    compiled_regex = re.compile(COMMAND_REGEX.format(username), re.IGNORECASE)
    match = compiled_regex.search(body.lower())
    if match:
        return {
            'rebase': ('rebase', 'rebased'),
            'merge': ('merge', 'merged'),
            'fastforward': ('fastforward', 'fastforwarded'),
            'ff': ('fastforward', 'fastforwarded')
        }.get(match.group(1), (None, None))
    return None, None


@ResponderRegistrar.responder('rebaser', MergeRequestActions.COMMENTED)
def apply_command_on_merge_request(
        pr: MergeRequest, comment: Comment,
        enable_rebase: bool=False,
        enable_merge: bool=False,
        enable_fastforward: bool=False
):
    """
    Performs a merge, fastforward or rebase of a merge request when an
    authorized user posts a command mentioning the keywords ``merge``,
    ``fastforward``/``ff`` or ``rebase`` respectively.

    e.g. ``@gitmate-bot rebase`` rebases the pull request with master.
    """
    username = Repository.from_igitt_repo(pr.repository).user.username
    cmd, cmd_past = get_matched_command(comment.body, username)
    enabled_cmd = {
        'rebase': enable_rebase,
        'merge': enable_merge,
        'fastforward': enable_fastforward
    }.get(cmd)

    if enabled_cmd:
        if not verify_command_access(comment, cmd):
            pr.add_comment(
                f'Hey @{comment.author.username}, you do not have the access '
                f'to perform the {cmd} action with [GitMate.io]'
                '(https://gitmate.io). Please ask a maintainer to give you '
                'access. :warning:')
            return

        pr.add_comment(
            f'Hey! I\'m [GitMate.io](https://gitmate.io)! This pull request is'
            f' being {cmd_past} automatically. Please **DO NOT** push while '
            f'{cmd} is in progress or your changes would be lost permanently '
            ':warning:')
        head_clone_url = pr.source_repository.clone_url
        base_clone_url = pr.target_repository.clone_url
        output = run_in_container(settings.REBASER_IMAGE,
                                  'python', 'run.py', cmd, head_clone_url,
                                  base_clone_url, pr.head_branch_name,
                                  pr.base_branch_name)
        output = json.loads(output)
        if output['status'] == 'success':
            pr.add_comment(
                f'Automated {cmd} with [GitMate.io](https://gitmate.io) was '
                'successful! :tada:')
        elif 'error' in output:
            # hiding oauth token for safeguarding user privacy
            error = output['error'].replace(head_clone_url,
                                            '<hidden_oauth_token>')
            error = error.replace(base_clone_url, '<hidden_oauth_token>')
            pr.add_comment(f'Automated {cmd} failed! Please {cmd} your pull '
                           'request manually via the command line.\n\n'
                           'Reason:\n```\n{}\n```'.format(error))
