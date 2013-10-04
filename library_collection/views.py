# views.py

from django.shortcuts import render
from django.core.urlresolvers import resolve
from library_collection.models import Collection, Campus, Repository
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from human_to_bytes import bytes2human
from django.db.models import Sum

campuses = Campus.objects.all().order_by('slug')

# view of collections in list. Currently home page
def collections(request, campus_slug=None):
    if campus_slug:
        campus = get_object_or_404(Campus, slug=campus_slug)
        extent = bytes2human( Collection.objects.filter(campus__slug__exact=campus.slug).aggregate(Sum('extent'))['extent__sum'] or 0)
        collections = Collection.objects.filter(campus__slug__exact=campus.slug).order_by('name')
    else:
        collections = Collection.objects.all().order_by('name')
        extent = bytes2human(Collection.objects.all().aggregate(Sum('extent'))['extent__sum'])
    return render(request,
        template_name='library_collection/index.html',
        dictionary = { 
            'collections': collections, 
            'extent': extent, 
            'campus': campus,
            'campuses': campuses, 
            'active_tab': active_tab(request),
            'current_path': request.path,
        },
        current_app = resolve(request.path).namespace,
    )

# view for collection details
def details(request, colid=None, col_slug=None):
    collection = get_object_or_404(Collection, pk=colid)
    # if the collection id matches, but the slug does not, redirect (for seo)
    if col_slug != collection.slug:
        return redirect(collection, permanent=True)
    else:
        return render(request,
            template_name='library_collection/collection.html',
            dictionary={ 
                'collection': collection,
                'campuses': campuses, 
            },
            current_app = resolve(request.path).namespace,
        )

def details_by_id(request, colid):
    collection = get_object_or_404(Collection, pk=colid)
    return redirect(collection, permanent=True)

def active_tab(request):
    '''Return a key for the active tab, by parsing the request.path
    Currently one of "collection" or "repositories"'''
    tab = 'collection'
    if "repositor" in request.path:
        tab = 'repositories'
    return tab

def repositories(request, campus_slug=None):
    '''View of repositories, for whole collection or just single campus'''
    campus = None
    if campus_slug:
        campus = get_object_or_404(Campus, slug=campus_slug)
        repositories = Repository.objects.filter(campus=campus)
    else:
        repositories = Repository.objects.all()
    return render(request,
            template_name='library_collection/repository_list.html',
            dictionary={
                'campus': campus,
                'repositories': repositories,
                'campuses': campuses, 
                'active_tab': active_tab(request),
                'current_path': request.path,
            },
            current_app = resolve(request.path).namespace,
    )
