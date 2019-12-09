
def active_tab(request):
    '''
    Return a key for the active tab into the default template context
    by parsing the request.path
    '''
    tab = 'collection'
    if "repositor" in request.path:
        tab = 'repositories'
    if "about" in request.path:
        tab = 'about'
    if "exhibitions" in request.path or "educators" in request.path:
        tab = 'exhibitions'
    return {
        'active_tab': tab
    }