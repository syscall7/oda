from time import time
from logging import getLogger
from itertools import count
from django.db import connection
from threading import local

logger = getLogger(__name__)

class LoggingMiddleware(object):
    def __init__(self):
        # arguably poor taste to use django's logger
        self.requestNum = count()
        self.logger = getLogger(__file__)

    def process_request(self, request):
        request.timer = time()
        request.requestNum = int(next(self.requestNum))
        self.logger.info("%s|%s", request.user.username , request.get_full_path())
        return None

    def process_response(self, request, response):
        requestNum = -1
        requestTime = -1
        if hasattr(request, 'requestNum'):
            requestNum = request.requestNum
        if hasattr(request, 'timer'):
            requestTime = time() - request.timer

        self.logger.info(
            '%s [%s] (%.1fs)',
            request.get_full_path(),
            response.status_code,
            requestTime
        )
        return response

class QueryCountDebugMiddleware(object):
    """
    This middleware will log the number of queries run
    and the total time taken for each request (with a
    status code of 200). It does not currently support
    multi-db setups.
    """
    def process_response(self, request, response):
        if response.status_code == 200:
            total_time = 0

            for query in connection.queries:
                query_time = query.get('time')
                if query_time is None:
                    # django-debug-toolbar monkeypatches the connection
                    # cursor wrapper and adds extra information in each
                    # item in connection.queries. The query time is stored
                    # under the key "duration" rather than "time" and is
                    # in milliseconds, not seconds.
                    query_time = query.get('duration', 0) / 1000
                total_time += float(query_time)

            logger.debug('%s queries run, total %s seconds' % (len(connection.queries), total_time))
        return response



_thread_locals = local()

def get_current_request():
    """ returns the request object for this thread """
    return getattr(_thread_locals, "request", None)


def get_current_user():
    """ returns the current user, if exist, otherwise returns None """
    request = get_current_request()
    if request:
        return getattr(request, "user", None)


class ThreadLocalMiddleware(object):
    """ Simple middleware that adds the request object in thread local storage."""
    def process_request(self, request):
        _thread_locals.request = request

    def process_response(self, request, response):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response