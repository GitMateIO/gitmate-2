from sys import exc_info
from traceback import format_exception

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpRequest

from gitmate_logger.models import Error


class LoggingExceptionHandler(object):
    """
    The logging exception handler.

    Django exposes all pythonic errors as Internal Server Error, which is no
    concrete class for exceptions. So, instead, we exclude the other possible
    exceptions from ``django.core.exceptions`` while reporting.
    """
    exclude = [PermissionDenied, ValidationError, Http404]

    @classmethod
    def create_from_exception(cls,
                              sender,
                              request: HttpRequest=None,
                              *args,
                              **kwargs):
        """
        Handles the exception upon receiving the signal.
        """
        kind, info, data = exc_info()
        # exclude unimportant errors
        if any([issubclass(kind, e) for e in cls.exclude]):
            return

        if request is not None:
            Error.objects.create(
                kind=kind.__name__,
                path=request.build_absolute_uri(),
                info=info,
                data='\n'.join(format_exception(kind, info, data)),
            ).save()
