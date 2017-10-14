import logging
from collections import defaultdict
from enum import Enum
from functools import wraps
from hashlib import sha1
from inspect import Parameter
from inspect import signature
from typing import Callable
import hmac

from django_rq import job
from django_rq import get_scheduler
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rq.job import Job

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
    :param event_name:  A string or enum for the type of event.
                        e.g. MergeRequestActions.COMMENTED
    :param is_active:   A boolean value for active state of plugin.
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

    :param key:                 The client key used to verify the hash.
    :param provider:            The provider for which hash is to be verified.
    :param http_header_name:    Name of HTTP request header which contains the
                                secure signature.
    :return:                    The response generated from the view.
    """
    def decorator(view: Callable):

        @wraps(view)
        def _view_wrapper(request: Request, *args, **kwargs):

            # key not found, verification turned off!
            if not key:
                logging.warning('Webhook signature verification turned off!'
                                'Please verify WEBHOOK_SECRET in settings.')
                return view(request, *args, **kwargs)

            # improper request structure
            if not all([http_header_name in request.META, len(request.body)]):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if provider == Providers.GITHUB.value:
                hashed = hmac.new(key.encode('utf-8'), request.body, sha1)
                generated_signature = hashed.hexdigest()
                sign = request.META[http_header_name]

                if generated_signature == sign[5:]:
                    return view(request, *args, **kwargs)

            elif provider == Providers.GITLAB.value:
                if request.META[http_header_name] == key:
                    return view(request, *args, **kwargs)

            # signature does not match
            return Response(status=status.HTTP_403_FORBIDDEN)

        return _view_wrapper
    return decorator


class ResponderRegistrar:
    """
    This class provides ability to register responders and invoke them.
    All responders belong to a plugin that can be activated per repository.

    The decorators which register the functions with RQ viz. ``scheduler``,
    ``scheduled_responder`` and ``responder``, do not take part in the
    function invocation themselves and are called by RQ. Hence, they return
    the function object as is and not it's return value. This means that the
    nature of function remains intact even after applying the decorator and
    hence, say goodbye to ``functools.wraps``.

    >>> from gitmate_hooks.utils import ResponderRegistrar
    >>> from IGitt.Interfaces.Actions import MergeRequestActions
    >>> @ResponderRegistrar.responder('test', MergeRequestActions.OPENED)
    ... def returner(s: str='Hello World!'):
    ...     '''The ultimate returning function'''
    ...     return s

    The nature of the function remains the same, although it works with RQ too
    as part of the ``ResponderRegistrar.respond`` call.

    >>> returner()
    'Hello World!'
    >>> returner('Squish them bugs!')
    'Squish them bugs!'
    >>> returner.__name__
    'returner'
    >>> returner.__doc__
    'The ultimate returning function'

    """

    _responders = defaultdict(list)
    _options = defaultdict(list)
    _plugins = {}

    @classmethod
    def scheduler(cls,
                  interval: str,
                  *args,
                  **kwargs): # pragma: no cover
        """
        Registers the decorated function as a periodic task. The task should
        not accept any arguments.

        :param interval:    A cron string.
                            e.g. '*/10 * * * *' executes job every 10 seconds
        :param args:        Arguments to pass to scheduled task.
        :param kwargs:      Keyword arguments to pass to scheduled task.
        """
        def _wrapper(function: Callable):
            get_scheduler().cron(interval, function)
            return function
        return _wrapper

    @classmethod
    def scheduled_responder(cls,
                            plugin: str,
                            interval: str,
                            **kwargs):
        """
        Registers the decorated function as responder and register
        `run_plugin_for_all_repos` as periodic task with plugin name and
        a responder event as arguments.

        :param plugin:      Name of plugin with which responder will be
                            registered.
        :param interval:    A cron string.
                            e.g. '*/10 * * * *' executes job every 10 seconds
        :param kwargs:      Keyword arguments to pass to
                            `run_plugin_for_all_repos`.

        >>> from gitmate_hooks.utils import ResponderRegistrar
        >>> @ResponderRegistrar.scheduled_responder('test', '*/10 * * * *')
        ... def test_responder(igitt_repo):
        ...     print('Hello, World!')

        This will register a `test.test_responder` responder and schedule
        `run_plugin_for_all_repos` with arguments `('test',
        'test.test_responder')` with 10 seconds interval.
        """
        def _wrapper(function: Callable):
            action = '{}.{}'.format(plugin, function.__name__)
            args = (plugin, action)
            func = cls.responder(*args)(function)
            scheduler = get_scheduler()
            scheduler.cron(interval, func, args=args, kwargs=kwargs)
            return func
        return _wrapper


    @classmethod
    def responder(cls, plugin_name: str, *actions: [Enum]):
        """
        Registers the decorated function as a responder to the actions
        provided. Specifying description as defaults on option specific args
        is mandatory.
        """
        def _wrapper(function):
            task = job(function)
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
                                 responder: Job,
                                 plugin: Plugin,
                                 repo: Repository) -> dict:
        """
        Filters the matching options for the given responder out of all the
        settings registered for the given plugin.
        """
        options = plugin.get_settings(repo)
        keys = set(cls._options[responder]) & set(options.keys())
        return dict(zip(keys, [options[k] for k in keys]))

    @classmethod
    def _get_responders(cls,
                        event: Enum,
                        repo: Repository=None,
                        plugin_name: str=None) -> [Job]:
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
            # filter options for responder from options of plugin it is
            # registered in, to avoid naming conflicts when two plugins have
            # the same model field. e.g. `stale_label`
            plugin = Plugin.objects.get(name=cls._plugins[responder])
            options_specified = cls._filter_matching_options(
                responder, plugin, repo)
            try:
                retvals.append(responder.delay(*args, **options_specified))
            except BaseException:  # pragma: no cover
                logging.exception(f'ERROR: A responder failed.\n'
                                  f'Responder:   {repr(responder)}\n'
                                  f'Args:        {repr(args)}\n'
                                  f'Options:     {repr(options_specified)}')
                LoggingExceptionHandler.create_from_exception(
                    __name__, responder.__name__)

        return retvals
