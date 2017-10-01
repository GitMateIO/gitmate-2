from collections import defaultdict
from enum import Enum
from hashlib import sha1
from inspect import Parameter
from inspect import signature
from traceback import print_exc
import hmac

from celery import Task
from celery.schedules import crontab
from celery.utils.log import get_logger
from rest_framework import status
from rest_framework.response import Response

from gitmate.celery import app as celery
from gitmate_config import GitmateActions
from gitmate_config import Providers
from gitmate_config.models import Plugin
from gitmate_config.models import Repository
from gitmate_logger.signals import LoggingExceptionHandler


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
    plugin = Plugin.objects.get(name=plugin_name)
    for repo in plugin.repository_set.filter(active=is_active):
        ResponderRegistrar.respond(event_name, repo, repo.igitt_repo)


def signature_check(key: str,
                    provider: str,
                    http_header_name: str):
    """
    Decorator for views that checks if the signature from request header
    matches the one registered for webhooks.
    """
    def decorator(function):

        def _view_wrapper(request, *args, **kwargs):
            if http_header_name in request.META:
                if provider == Providers.GITHUB.value:
                    hashed = hmac.new(key.encode('utf-8'), request.body, sha1)
                    generated_signature = hashed.hexdigest()
                    sign = request.META[http_header_name]

                    if generated_signature == sign[5:]:
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
        logger.warning(warning)
        super().on_failure(exc, task_id, args, kwargs, einfo)


class ResponderRegistrar:
    """
    This class provides ability to register responders and invoke them.

    All responders belong to a plugin that can be activated per repository.
    """

    _responders = defaultdict(list)
    _options = defaultdict(list)
    _plugins = {}

    @classmethod
    def scheduler(cls,
                  interval: (crontab, float),
                  *args,
                  **kwargs): # pragma: no cover
        """
        Registers the decorated function as a periodic task.
        The task should not accept any arguments.

        :param interval:    Periodic interval in seconds as float or crontab
                            object specifying task trigger time.
                            See http://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab
        :param args:        Arguments to be passed to scheduled task.
        :param kwargs:      Keyword arguments to be passed to scheduled task.
        """
        def _wrapper(function):
            task = celery.task(function, base=ExceptionLoggerTask)
            celery.add_periodic_task(interval, task.s(), args, kwargs)
            return function

        return _wrapper

    @classmethod
    def scheduled_responder(cls,
                            plugin_name: str,
                            interval: (crontab, float),
                            **kwargs):
        """
        Registers the decorated function as responder and register
        `run_plugin_for_all_repos` as periodic task with plugin name and
        a responder event as arguments.

        :param plugin_name:     Name of plugin with which responder will be
                                registered.
        :param interval:        Periodic interval in seconds as float or crontab
                                object specifying task trigger time.
                                See http://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab
        :param kwargs:          Keyword arguments to be passed to
                                `run_plugin_for_all_repos`.

        >>> from gitmate_hooks.utils import ResponderRegistrar
        >>> @ResponderRegistrar.scheduled_responder('test', 10.0)
        ... def test_responder(igitt_repo):
        ...     print('Hello, World!')

        This will register a `test.test_responder` responder and schedule
        `run_plugin_for_all_repos` with arguments `('test',
        'test.test_responder')` with 10 seconds interval.
        """
        def _wrapper(function):
            action = '{}.{}'.format(plugin_name, function.__name__)
            periodic_task_args = (plugin_name, action)
            function = cls.responder(plugin_name, action)(function)
            task = celery.task(run_plugin_for_all_repos, base=ExceptionLoggerTask)
            celery.add_periodic_task(interval, task.s(), periodic_task_args, kwargs)
            return function

        return _wrapper

    @classmethod
    def responder(cls, plugin_name: str, *actions: [Enum]):
        """
        Registers the decorated function as a responder to the actions
        provided. Specifying description as defaults on option specific args
        is mandatory.

        :param plugin_name: The name of the plugin the responder is present in.
        :param actions:     The actions for which the responder is to be
                            executed.
        """
        def _wrapper(function):
            task = celery.task(function, base=ExceptionLoggerTask)
            for action in actions:
                cls._responders[action].append(task)
            cls._plugins[task] = plugin_name
            params = signature(function).parameters.values()
            cls._options[task] = [param.name for param in params
                                  if param.default is not Parameter.empty]
            return function
        return _wrapper

    @classmethod
    def _filter_matching_options(cls,
                                 responder: ResponderRegistrar.responder,
                                 plugin: Plugin,
                                 repo: Repository):
        """
        Filters the options for the given responder from all of the options in
        the plugin.
        """
        options = plugin.get_settings(repo)
        keys = set(cls._options[responder]) & set(options.keys())
        return dict(zip(keys, [options[k] for k in keys]))

    @classmethod
    def _get_responders(cls,
                        event: Enum,
                        repo: Repository=None,
                        plugin_name: str=None):
        """
        Retrieves the list of responders for the specified event. Filters only
        the ones within a plugin, if ``plugin name`` is specified. Filters only
        for responders active on a repository, if ``repo`` is specified.
        """
        responders = cls._responders.get(event, [])
        plugin_filter = lambda r: plugin_name == cls._plugins[r]
        repo_filter = lambda r: repo.plugins.filter(
            name=cls._plugins[r]).exists()

        if repo is not None and isinstance(repo, Repository):
            responders = list(filter(repo_filter, responders))

        if plugin_name:
            responders = list(filter(plugin_filter, responders))

        return responders

    @classmethod
    def respond(cls,
                event: Enum,
                repo: Repository,
                *args,
                plugin_name: str=None):
        """
        Invoke all responders for the given event. If a plugin name is
        specified, invokes responders only within that plugin.
        """
        retvals = []
        if isinstance(event, GitmateActions):
            responders = cls._get_responders(event, plugin_name=plugin_name)
        else:
            responders = cls._get_responders(event, repo=repo)

        for responder in responders:
            # Provide the options for the specified plugin
            plugin = Plugin.objects.get(name=cls._plugins[responder])
            options_specified = cls._filter_matching_options(
                responder, plugin, repo)
            try:
                retvals.append(responder.delay(*args, **options_specified))
            except BaseException:  # pragma: no cover
                print('ERROR: A responder failed.')
                print('Responder:   {0!r}'.format(responder))
                print('Args:        {0!r}'.format(args))
                print('Options:     {0!r}'.format(options_specified))
                print_exc()
                LoggingExceptionHandler.create_from_exception(
                    __name__, responder.name)

        return retvals
