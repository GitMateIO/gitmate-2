from enum import Enum
from hashlib import sha1
import hmac
from inspect import getfullargspec
from traceback import print_exc

from celery.schedules import crontab
from celery import Task
from celery.utils.log import get_logger
from rest_framework import status
from rest_framework.response import Response
from gitmate_config import Providers

from gitmate.celery import app as celery

def run_plugin_for_all_repos(plugin_name: str,
                             event_name: (str, Enum),
                             is_active: bool=True):
    """
    This will trigger the responders registered with `event_name`
    for every repo based on active state of a plugin.
    :param plugin_name: A string containing name of the plugin to check.
    :param event_name: A string or enum for the type of event.
                       e.g. MergeRequestActions.COMMENTED
    :is_active: A boolean value for active state of plugin.
    """
    from gitmate_config.models import Plugin

    plugin = Plugin.objects.get(name=plugin_name)
    for repo in plugin.repository_set.filter(active=is_active):
        ResponderRegistrar.respond(
            event_name,
            repo,
            repo.igitt_repo,
            options=repo.get_plugin_settings())

def signature_check(key: str=None,
                    provider: str=None,
                    http_header_name: str=None):
    """
    Decorator for views that checks if the signature from request header
    matches the one registered for webhooks.
    """
    def decorator(function):

        def _view_wrapper(request, *args, **kwargs):
            if key and http_header_name in request.META:
                if provider == Providers.GITHUB.value:
                    hashed = hmac.new(bytes(key, 'utf-8'), request.body, sha1)
                    generated_signature = hashed.hexdigest()
                    signature = request.META[http_header_name]

                    if generated_signature == signature[5:]:
                        return function(request, *args, **kwargs)

                elif provider == Providers.GITLAB.value:
                    if request.META[http_header_name] == key:
                        return function(request, *args, **kwargs)

            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return _view_wrapper

    return decorator

class ExceptionLoggerTask(Task):
    """
    Celery Task subclass to log exceptions on failure.
    
    For Task inheritance see:
    http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-inheritance
    """
    def on_failure(self, exc , task_id, args, kwargs, einfo):# pragma: no cover
        logger = get_logger('celery.worker')
        warning = ('Task {task}[{t_id}] had unexpected failure:\n'
                   '\nargs: {args}\n\nkwargs: {kwargs}\n'
                   '\n{einfo}').format(task=self.name,
                                         t_id=task_id,
                                         args=args,
                                         kwargs=kwargs,
                                         einfo=einfo)
        logger.warn(warning)
        super().on_failure(exc, task_id, args, kwargs, einfo)

class ResponderRegistrar:
    """
    This class provides ability to register responders and invoke them.

    All responders belong to a plugin that can be activated per repository.
    """

    _responders = {}
    _options = {}
    _plugins = {}

    @classmethod
    def scheduler(cls,
                  interval: (crontab, float),
                  *args,
                  **kwargs): # pragma: no cover
        """
        Registers the decorated function as a periodic task.
        The task should not accept any arguments.
        :param interval: Periodic interval in seconds as float or
                crontab object specifying task trigger time.
                See http://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab
        :param args: Arguments to pass to scheduled task.
        :param kwargs: Keyword arguments to pass to scheduled task.
        """
        def _wrapper(function):
            task = celery.task(function, base=ExceptionLoggerTask)
            celery.add_periodic_task(interval, task.s(), args, kwargs)
            return function

        return _wrapper

    @classmethod
    def scheduled_responder(cls,
                            plugin: str,
                            interval: (crontab, float),
                            **kwargs):
        """
        Registers the decorated function as responder and register 
        `run_plugin_for_all_repos` as periodic task with plugin name and
        a responder event as arguments.

        :param plugin: Name of plugin with which responder will be registered.
        :param interval: Periodic interval in seconds as float or crontab
                object specifying task trigger time.
                See http://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab
        :param kwargs: Keyword arguments to pass to `run_plugin_for_all_repos`.

        >>> from gitmate_hooks import ResponderRegistrar
        >>> @ResponderRegistrar.scheduled_responder('test', 10.0)
        ... def test_responder(igitt_repo):
        ...     print('Hello, World!')

        This will register a `test.test_responder` responder and schedule
        `run_plugin_for_all_repos` with arguments `('test',
        'test.test_responder')` with 10 seconds interval.
        """
        def _wrapper(function):
            action = '{}.{}'.format(plugin, function.__name__)
            periodic_task_args = (plugin, action)
            function = cls.responder(plugin, action)(function)
            task = celery.task(run_plugin_for_all_repos, base=ExceptionLoggerTask)
            celery.add_periodic_task(interval, task.s(), periodic_task_args, kwargs)
            return function

        return _wrapper


    @classmethod
    def responder(cls, plugin: str='', *actions: [Enum]):
        """
        Registers the decorated function as a responder to the actions
        provided. Specifying description as defaults on option specific args
        is mandatory.
        """
        def _wrapper(function):
            task = celery.task(function, base=ExceptionLoggerTask)

            for action in actions:
                if action not in cls._responders:
                    cls._responders[action] = []

                cls._responders[action].append(task)

            cls._plugins[task] = plugin

            argspec = getfullargspec(function)
            if argspec.defaults is not None:
                cls._options[task] = argspec.args[-len(argspec.defaults):]
            else:
                cls._options[task] = []
            return function

        return _wrapper

    @classmethod
    def options(cls):
        """
        Creates a dictionary of all registered responders associated with
        their corresponding option dictionaries.
        """
        return cls._options

    @classmethod
    def respond(cls, event, repo, *args, options={}):
        """
        Invoke all responders for the given event with the provided options.
        """
        retvals = []
        for responder in cls._responders.get(event, []):
            # Provide the options it wants
            options_specified = {}
            for option in cls.options()[responder]:
                if option in options:
                    options_specified[option] = options[option]

            # check if plugin is active on the repo
            plugin = cls._plugins[responder]
            if repo.plugins.filter(name=plugin).exists() is False:
                continue

            try:
                retvals.append(responder.delay(*args, **options_specified))
            except BaseException:  # pragma: no cover
                print('ERROR: A responder failed.')
                print('Responder:   {0!r}'.format(responder))
                print('Args:        {0!r}'.format(args))
                print('Options:     {0!r}'.format(options_specified))
                print_exc()

        return retvals
