from django.conf import settings

try:
    username = settings.REMOTE_USER_MOCK_USERNAME
except AttributeError:
    username  = 'test_superuser'
try:
    paths_locked = settings.REMOTE_USER_MOCK_PATHS
except AttributeError:
    paths_locked = ['/edit', '/admin']

class RemoteUserMockMiddleware(object):
    '''Mock a remote user, maybe want to prompt user.
    '''
    def process_request(self, request):
        for path in paths_locked:
            if request.path.startswith(path):
                request.META['REMOTE_USER'] = username
                return None

from django.http import HttpResponse
#http://djangosnippets.org/snippets/2468/
class BasicAuthMockMiddleware(object):
    def unauthed(self):
        response = HttpResponse("""<html><title>Auth required</title><body>
                                <h1>Authorization
                                Required</h1></body></html>""")
        response['WWW-Authenticate'] = 'Basic realm="Development"'
        response.status_code = 401
        return response

    def process_request(self,request):
        for path in paths_locked:
            if request.path.startswith(path):
                if not request.META.has_key('HTTP_AUTHORIZATION'):
                    return self.unauthed()
                else:
                    authentication = request.META['HTTP_AUTHORIZATION']
                    (authmeth, auth) = authentication.split(' ',1)
                    if 'basic' != authmeth.lower():
                        return self.unauthed()
                    auth = auth.strip().decode('base64')
                    username, password = auth.split(':',1)
                    ## let anything through and set REMOTE_USER
                    request.META['REMOTE_USER'] = username
                    # The next bits are so this will pass the
                    # RegistryUserBackend
                    request.META['mail'] = "mark.redar@ucop.edu" if not hasattr(settings, 'REMOTE_USER_MOCK_EMAIL') else settings.REMOTE_USER_MOCK_EMAIL
                    request.META['Shib-Identity-Provider'] = 'test'
        return None
