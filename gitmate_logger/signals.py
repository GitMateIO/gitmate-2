from sys import exc_info
from traceback import format_exception

from django.views.debug import ExceptionReporter
from django.http import Http404
from django.http import HttpRequest

from gitmate_logger.models import Error


class LoggingExceptionHandler(object):
    """
    The logging exception handler.
    """
    @staticmethod
    def create_from_exception(sender,
                              request:(str, HttpRequest)=None,
                              *args,
                              **kwargs):
        """
        Handles the exception upon receiving the signal.
        """
        kind, info, data = exc_info()
        path = None

        if isinstance(request, str):
            path = request
        elif request is not None:
            path = request.build_absolute_uri()

        # do not log HTTP 404 errors
        if not issubclass(kind, Http404):
            Error.objects.create(
                kind=kind.__name__,
                path=path,
                info=info,
                data='\n'.join(format_exception(kind, info, data)),
            ).save()
