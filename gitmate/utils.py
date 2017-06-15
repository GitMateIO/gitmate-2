from contextlib import contextmanager

import logging


@contextmanager
def lock_igitt_object(task: str, igitt_object):
    """
    The IGitt object should have an .url property, so right now this will only
    work with issues and merge requests.
    """
    from db_mutex import DBMutexError, DBMutexTimeoutError
    from db_mutex.db_mutex import db_mutex

    try:
        with db_mutex(task + igitt_object.url):
            igitt_object.refresh()
            yield
    except DBMutexError:  # pragma: no cover
        logging.error('Failed to acquire lock for {} for {}'.format(
            task, igitt_object.url))
    except DBMutexTimeoutError:  # pragma: no cover
        logging.error('Timeout while acquiring lock for {} for {}'.format(
            task, igitt_object.url))
