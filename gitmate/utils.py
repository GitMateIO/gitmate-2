from contextlib import contextmanager


from django_pglocks import advisory_lock


@contextmanager
def lock_igitt_object(task: str, igitt_object):
    """
    The IGitt object should have an .url property, so right now this will only
    work with issues and merge requests.
    """
    with advisory_lock(task + igitt_object.url):
        igitt_object.refresh()
        yield
