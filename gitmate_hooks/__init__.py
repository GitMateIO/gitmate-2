from enum import Enum
from hashlib import sha1
import hmac
from inspect import getfullargspec
from traceback import print_exc

from rest_framework import status
from rest_framework.response import Response


def signature_check(key: str=None, http_header_name: str=None):
    """
    Decorator for views that checks if the signature from request header
    matches HMAC hexdigest of the request body.
    """
    def decorator(function):

        def _view_wrapper(request, *args, **kwargs):
            if key and http_header_name in request.META:
                hashed = hmac.new(bytes(key, 'utf-8'), request.body, sha1)
                generated_signature = hashed.hexdigest()
                signature = request.META[http_header_name]

                if generated_signature == signature[5:]:
                    return function(request, *args, **kwargs)

            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return _view_wrapper

    return decorator


class ResponderRegistrar:
    """
    This class provides ability to register responders and invoke them.

    All responders belong to a plugin that can be activated per repository.
    """

    _responders = {}
    _options = {}
    _plugins = {}

    @classmethod
    def responder(cls, plugin: str='', *actions: [Enum]):
        """
        Registers the decorated function as a responder to the actions
        provided. Specifying description as defaults on option specific args
        is mandatory.
        """
        def _wrapper(function):
            for action in actions:
                if action not in cls._responders:
                    cls._responders[action] = []

                cls._responders[action].append(function)

            cls._plugins[function] = plugin

            argspec = getfullargspec(function)
            if argspec.defaults is not None:
                cls._options[function] = argspec.args[-len(argspec.defaults):]
            else:
                cls._options[function] = []
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
                retvals.append(responder(*args, **options_specified))
            except BaseException:  # pragma: no cover
                print('ERROR: A responder failed.')
                print('Responder:   {0!r}'.format(responder))
                print('Args:        {0!r}'.format(args))
                print('Options:     {0!r}'.format(options_specified))
                print_exc()

        return retvals
