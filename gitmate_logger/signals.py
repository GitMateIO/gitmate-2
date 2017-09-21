from sys import exc_info
from traceback import format_exception

from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import HttpRequest
from django.views.debug import ExceptionReporter

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
                              request:(str, HttpRequest)=None,
                              *args,
                              **kwargs):
        """
        Handles the exception upon receiving the signal.
        """
        kind, info, data = exc_info()

        # exclude unimportant errors
        if any([issubclass(kind, e) for e in cls.exclude]):
            return

        path = None
        if isinstance(request, str):
            path = request
        elif request is not None:
            path = request.build_absolute_uri()

        Error.objects.create(
            kind=kind.__name__,
            path=path,
            info=info,
            data='\n'.join(format_exception(kind, info, data)),
        ).save()
