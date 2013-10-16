# views.py

from django.shortcuts import render
from library_collection.models import Collection, Campus, Repository
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from human_to_bytes import bytes2human
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

campuses = Campus.objects.all().order_by('name')

def active_tab(request):
    '''Return a key for the active tab, by parsing the request.path
    Currently one of "collection" or "repositories"'''
    tab = 'collection'
    if "repositor" in request.path:
        tab = 'repositories'
    return tab

def editing(path):
    '''Return whether we are editing or not. In the real app, a user will only
    be logged in when at an editing URL. This helper function will enable
    us to tell the difference between edit & read-only interfaces when
    testing.
    '''
    return True if path.split('/', 2)[1].strip('/') == 'edit' else False

@login_required
def edit_collections(request, campus_slug=None):
    '''Edit view of all collections. Only difference from read-only is the 
    "add" link/button.
    '''
    if (request.method == 'POST'):
        requestObj = request.POST
        if ('edit' in requestObj):
            context = {
                'campuses': campuses,
                'current_path': request.path,
                'editing': editing(request.path),
                'repositories': Repository.objects.all().order_by('name'),
                'appendixChoices': Collection.APPENDIX_CHOICES,
                'edit': 'true',
            }
            return render(request,
                template_name='library_collection/new_collection.html',
                dictionary=context
            )
        else: 
            new_collection = Collection()
            new_collection.name = requestObj['name']
            new_collection.appendix = requestObj['appendix']
            new_collection.save();
            new_collection.repository = requestObj.getlist('repositories')
            new_collection.campus = requestObj.getlist('campuses')
            return redirect(reverse('edit_detail',
                    kwargs={ 'colid': new_collection.pk,
                        'col_slug': new_collection.slug }
                ))
            
    return collections(request, campus_slug)

# view of collections in list. Currently home page
def collections(request, campus_slug=None):
    campus = None
    if campus_slug:
        campus = get_object_or_404(Campus, slug=campus_slug)
        extent = bytes2human( Collection.objects.filter(campus__slug__exact=campus.slug).aggregate(Sum('extent'))['extent__sum'] or 0)
        collections = Collection.objects.filter(campus__slug__exact=campus.slug).order_by('name')
    else:
        collections = Collection.objects.all().order_by('name')
        extent = bytes2human(Collection.objects.all().aggregate(Sum('extent'))['extent__sum'])
    return render(request,
        template_name='library_collection/collection_list.html',
        dictionary = { 
            'collections': collections, 
            'extent': extent, 
            'campus': campus,
            'campuses': campuses, 
            'active_tab': active_tab(request),
            'current_path': request.path,
            'editing': editing(request.path),
        },
    )

@login_required
def edit_details(request, colid=None, col_slug=None):
    collection = get_object_or_404(Collection, pk=colid)
    if col_slug != collection.slug:
        return redirect(collection, permanent=True)
    else:
        context = {
            'collection': collection,
            'current_path': request.path,
            'editing': editing(request.path),
        }
        if (request.method == 'POST'):
            requestObj = request.POST
            if ('edit' in requestObj):
                context['campuses'] = campuses
                context['repositories'] = Repository.objects.all().order_by('name')
                context['appendixChoices'] = Collection.APPENDIX_CHOICES
                context['edit'] = 'true'
                return render(request,
                    template_name='library_collection/collection_edit.html',
                    dictionary=context
                )
            else: 
                collection.name = requestObj["name"]
                collection.appendix = requestObj['appendix']
                collection.repository.clear()
                collection.repository = requestObj.getlist('repositories')
                collection.campus = requestObj.getlist("campuses")
                collection.save();
    
        return render(request,
            template_name='library_collection/collection.html',
            dictionary=context
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
                'current_path': request.path,
                'editing': editing(request.path),
            },
        )

@login_required
def edit_details_by_id(request, colid):
    return details_by_id(request, colid)

def details_by_id(request, colid):
    collection = get_object_or_404(Collection, pk=colid)
    return redirect(collection, permanent=True)

@login_required
def edit_repositories(request, campus_slug=None):
    return repositories(request, campus_slug)

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
                'editing': editing(request.path),
            },
    )
