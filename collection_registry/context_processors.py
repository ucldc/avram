
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
        'active_tab': active_tab(request),
        'exhibitBaseTemplate': settings.EXHIBIT_TEMPLATE,
        'thumbnailUrl': settings.THUMBNAIL_URL,
        'calisphere': settings.CALISPHERE
    }