from contextlib import contextmanager


@contextmanager
def lock_igitt_object(task: str, igitt_object):
    """
    The IGitt object should have an .url property, so right now this will only
    work with issues and merge requests.

    TEMPORARY NOT LOCKING THINGS, just yielding. We'll have to figure out a way
    to fix :/ Check git history for original code.

    django.db.utils.IntegrityError: duplicate key value violates unique
    constraint "db_mutex_dbmutex_lock_id_key"
    DETAIL:  Key (lock_id)=(label mrhttps://gitlab.com/gitmate-bot/anothertest/
    merge_requests/2) already exists.
    """
    yield
