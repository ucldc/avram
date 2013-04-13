# views.py

from django.shortcuts import render_to_response
from library_collection.models import ProvenancialCollection, Campus
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from human_to_bytes import bytes2human
from django.db.models import Sum

campuses = Campus.objects.all().order_by('slug')

# view for home page
def home(request):
    collections = ProvenancialCollection.objects.all().order_by('name')
    raw_extent = ProvenancialCollection.objects.all().aggregate(Sum('extent'))['extent__sum']
    extent = bytes2human( raw_extent )
    
    return render_to_response(
        'library_collection/index.html', { 
            'collections': collections, 
            'extent': extent, 
            'campuses': campuses, 
        }
    )

# view for collection details
def details(request, colid, urlstuff):
    collection = get_object_or_404(ProvenancialCollection, pk=colid)
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
    collection = get_object_or_404(ProvenancialCollection, pk=colid)
    return redirect(collection, permanent=True)

#view for a UC campus
def UC(request, urlstuff):
    campus = get_object_or_404(Campus, slug=urlstuff)
    extent = bytes2human( ProvenancialCollection.objects.filter(campus__slug__exact=urlstuff).aggregate(Sum('extent'))['extent__sum'] or 0)
    collections = ProvenancialCollection.objects.filter(campus__slug__exact=urlstuff).order_by('name')
    return render_to_response(
        'library_collection/campus.html', {
            'campus': campus, 
            'collections': collections, 
            'extent': extent, 
            'campuses': campuses, 
        }
    )

