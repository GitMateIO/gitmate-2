import logging
from difflib import SequenceMatcher

from IGitt.Interfaces.Actions import IssueActions
from IGitt.Interfaces.Issue import Issue

from gitmate_hooks import ResponderRegistrar


def matches(expression, pattern, min_match_ratio=0.8):
    """
    Verifies if the expression matches pattern atleast to the specified minimum
    match ratio.

    >>> matches("I love apples", "apples", 1.0)
    True
    >>> matches("I love aplpes", "apples")
    True
    >>> matches("I lov apples", "lov apples")
    True
    >>> matches("I love apples", "lobster")
    False

    :param expression:
        String that is to be checked for acceptance.
    :param pattern:
        String to be matched against.
    :param min_match_ratio:
        Minimum match ratio to accept the expression.

    :return bool:
        Returns true if the match is successful, else false.
    """
    for left in range(len(expression) - len(pattern) + 1):
        right = left + len(pattern)
        ratio = SequenceMatcher(a=expression[left:right], b=pattern).ratio()
        if ratio >= min_match_ratio:
            return True
    return False


@ResponderRegistrar.responder('issue_labeller', IssueActions.OPENED)
def add_labels_to_issue(
    issue: Issue,
    blacklisted_labels: [str] = 'Labels which should not be used'
):
    # Inline import needed because this file is imported beore the db mutex
    # django app is initialized
    from gitmate.utils import lock_igitt_object

    issue_summary = issue.title.lower() + ' ' + issue.description.lower()

    with lock_igitt_object('issue labelling', issue):
        new_labels = set({
            label for label in issue.available_labels
            if matches(issue_summary, label, 0.9) and
            label not in blacklisted_labels})

        issue.labels = new_labels.union(issue.labels)
