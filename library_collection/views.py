# views.py

from django.shortcuts import render_to_response
from library_collection.models import Collection, Campus, Repository
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from human_to_bytes import bytes2human
from django.db.models import Sum

campuses = Campus.objects.all().order_by('slug')

# view for home page
def home(request):
    collections = Collection.objects.all().order_by('name')
    raw_extent = Collection.objects.all().aggregate(Sum('extent'))['extent__sum']
    extent = bytes2human( raw_extent )
    
    return render_to_response(
        'library_collection/index.html', { 
            'collections': collections, 
            'extent': extent, 
            'campuses': campuses, 
	    'active_tab': active_tab(request),
        }
    )

# view for collection details
def details(request, colid, urlstuff):
    collection = get_object_or_404(Collection, pk=colid)
    # if the collection id matches, but the slug does not, redirect (for seo)
    if urlstuff != collection.slug:
        return redirect(collection, permanent=True)
    else:
        return render_to_response(
            'library_collection/collection.html', { 
                'collection': collection,
                'campuses': campuses, 
            }
        )

def details_by_id(request, colid):
    collection = get_object_or_404(Collection, pk=colid)
    return redirect(collection, permanent=True)

def active_tab(request):
    '''Return a key for the active tab, by parsing the request.path
    Currently one of "collection" or "repository"'''
    tab = 'collection'
    if "repositor" in request.path:
        tab = 'repositories'
    return tab

def repositories(request, campus=None):
    '''View of repositories, for whole collection or just single campus'''
    if campus:
        campus = get_object_or_404(Campus, slug=campus)
        repositories = Repository.objects.filter(campus=campus)
    else:
        repositories = Repository.objects.all()
    return render_to_response(
	'library_collection/repository_list.html', {
	'campus': campus,
	'repositories': repositories,
        'campuses': campuses, 
	'active_tab': active_tab(request),
        }
    )
	

#view for a UC campus
def UC(request, urlstuff):
    campus = get_object_or_404(Campus, slug=urlstuff)
    extent = bytes2human( Collection.objects.filter(campus__slug__exact=urlstuff).aggregate(Sum('extent'))['extent__sum'] or 0)
    collections = Collection.objects.filter(campus__slug__exact=urlstuff).order_by('name')
    return render_to_response(
        'base.html', {
            'campus': campus, 
            'collections': collections, 
            'extent': extent, 
            'campuses': campuses, 
	    'active_tab': active_tab(request),
        }
    )

