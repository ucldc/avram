# https://docs.djangoproject.com/en/2.2/topics/http/middleware/#upgrading-middleware
from django.utils.deprecation import MiddlewareMixin

# http://stackoverflow.com/a/1057418/1763984
import threading
_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class ThreadLocals(MiddlewareMixin):
    """
    Middleware that gets various objects from the
    request object and saves them in thread local storage.
    """
    def process_request(self, request):
        _thread_locals.request = request
