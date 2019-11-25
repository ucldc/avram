
from future import standard_library
standard_library.install_aliases()
import urllib.parse


def settings(request):
    """
    Put selected settings variables into the default template context
    """
    from django.conf import settings

    def active_tab(request):
        '''Return a key for the active tab, by parsing the request.path
        Currently one of "collection" or "repositories"'''
        tab = 'collection'
        if "repositor" in request.path:
            tab = 'repositories'
        if "about" in request.path:
            tab = 'about'
        if "exhibitions" in request.path or "educators" in request.path:
            tab = 'exhibitions'
        return tab

    return {
        'thumbnailUrl': settings.THUMBNAIL_URL,
        'active_tab': active_tab(request),
        'exhibitBaseTemplate': 'exhibitBase.html', 
        'calisphere': False
    }
