# views.py

from django.shortcuts import render
from library_collection.models import Collection, Campus, Repository
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from human_to_bytes import bytes2human
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from library_collection.decorators import verification_required
from django.core.exceptions import ValidationError

campuses = Campus.objects.all().order_by('position')

def active_tab(request):
    '''Return a key for the active tab, by parsing the request.path
    Currently one of "collection" or "repositories"'''
    tab = 'collection'
    if "repositor" in request.path:
        tab = 'repositories'
    if "about" in request.path:
        tab = 'about'
    return tab

def editing(path):
    '''Return whether we are editing or not. In the real app, a user will only
    be logged in when at an editing URL. This helper function will enable
    us to tell the difference between edit & read-only interfaces when
    testing.
    '''
    return True if path.split('/', 2)[1].strip('/') == 'edit' else False

@login_required
@verification_required
def edit_collections(request, campus_slug=None, error=None):
    '''Edit view of all collections. Only difference from read-only is the 
    "add" link/button.
    '''
    if (request.method == 'POST'):
        requestObj = request.POST
        if ('new' in requestObj or error):
            context = {
                'campuses': campuses,
                'current_path': request.path,
                'editing': editing(request.path),
                'repositories': Repository.objects.all().order_by('name'),
                'appendixChoices': Collection.APPENDIX_CHOICES,
                'new': 'true',
            }
            if error:
                context['error'] = error
                
                collection = {'name': requestObj['name']}
                if 'appendix' in requestObj:
                    collection['appendix'] = requestObj['appendix']
                if 'campuses' in requestObj:
                    campus = []
                    for campus_id in requestObj.getlist('campuses'):
                        campus.append(Campus.objects.get(pk=campus_id))
                    collection['campus'] = campus
                if 'repositories' in requestObj:
                    repository = []
                    for repository_id in requestObj.getlist('repositories'):
                        repository.append(Repository.objects.get(pk=repository_id))
                    collection['repository'] = repository
                context['collection'] = collection
                
            return render(request,
                template_name='library_collection/collection_edit.html',
                dictionary=context
            )
        else: 
            try:
                new_collection = Collection(name=requestObj['name'], appendix=requestObj['appendix'])
                new_collection.full_clean()
            except ValidationError as e:
                return edit_collections(request, error='Please enter a collection title')
            except KeyError as e:
                return edit_collections(request, error='Please enter a data source')
            
            if len(requestObj.getlist('campuses')) < 1:
               return edit_collections(request, error='Please enter at least one campus')
            
            new_collection.save()
            new_collection.repository = requestObj.getlist('repositories')
            new_collection.campus = requestObj.getlist('campuses')
            return edit_details(request, new_collection.pk, new_collection.slug)
            
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
@verification_required
def edit_details(request, colid=None, col_slug=None, error=None):
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
            if ('edit' in requestObj) or error:
                context['campuses'] = campuses
                context['repositories'] = Repository.objects.all().order_by('name')
                context['appendixChoices'] = Collection.APPENDIX_CHOICES
                context['edit'] = 'true'
                
                if error:
                    context['error'] = error
                    collection.name = requestObj['name']
                    collection.campus = requestObj.getlist('campuses')
                    collection.repository = requestObj.getlist('repositories')
                    
                    if requestObj['name'] == '':
                        context['error'] = "Please enter a collection title"
                    if 'appendix' in requestObj:
                        collection.appendix = requestObj['appendix']
                    else: 
                        context['error'] = "Please enter a data source"
                    
                    context['collection'] = collection
                
                return render(request,
                    template_name='library_collection/collection_edit.html',
                    dictionary=context
                )
            else: 
                collection.name = requestObj.get("name")
                collection.appendix = requestObj.get('appendix')
                collection.repository = requestObj.getlist('repositories')
                collection.campus = requestObj.getlist("campuses")
                
                if len(requestObj.getlist("campuses")) < 1:
                   return edit_details(request, colid, col_slug, error="Please enter at least one campus")
                
                try:
                    collection.full_clean()
                except ValidationError as e:
                    return edit_details(request, colid, col_slug, error=e)
                
                collection.save()
    
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
@verification_required
def edit_details_by_id(request, colid):
    return details_by_id(request, colid)

def details_by_id(request, colid):
    collection = get_object_or_404(Collection, pk=colid)
    return redirect(collection, permanent=True)

@login_required
@verification_required
def edit_repositories(request, campus_slug=None, error=None):
    campus = None
    if campus_slug:
        campus = get_object_or_404(Campus, slug=campus_slug)
        repositoryObjs = Repository.objects.filter(campus=campus).order_by('name')
    else:
        repositoryObjs = Repository.objects.all().order_by('name')
        
    if (request.method == 'POST'):
        requestObj = request.POST
        if ('edit' in requestObj or error):
            context = {
                'campuses': campuses,
                'current_path': request.path,
                'editing': editing(request.path),
                'edit': 'true',
                'repositories': repositoryObjs
            }
            if error:
                context['error'] = error
                if 'campuses' in requestObj:
                    campus = []
                    for campus_id in requestObj.getlist('campuses'):
                        campus.append(Campus.objects.get(pk=campus_id))
                    context['campus_list'] = campus
                if 'name' in requestObj:
                    context['repository'] = {'name': requestObj['name']}
                
            return render(request,
                template_name='library_collection/repository_list.html',
                dictionary=context
            )
        else: 
            try: 
                new_repository = Repository(name = requestObj['name'])
                validated = new_repository.full_clean()
            except ValidationError as e:
                return edit_repositories(request, error='Please enter a unit title')
            
            if len(requestObj.getlist('campuses')) < 1:
               return edit_repositories(request, error='Please enter at least one campus')
            
            new_repository.save()
            new_repository.campus = requestObj.getlist('campuses')
            
            return render(request, template_name='library_collection/repository_list.html', 
                dictionary={
                    'campus': campus,
                    'repositories': repositoryObjs,
                    'campuses': campuses,
                    'active_tab': active_tab(request),
                    'current_path': request.path,
                    'editing': editing(request.path),
                },
            )
    
    return repositories(request, campus_slug)

def repositories(request, campus_slug=None):
    '''View of repositories, for whole collection or just single campus'''
    campus = None
    if campus_slug:
        campus = get_object_or_404(Campus, slug=campus_slug)
        repositories = Repository.objects.filter(campus=campus).order_by('name')
    else:
        repositories = Repository.objects.all().order_by('name')
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

@login_required
@verification_required
def edit_about(request):
    return about(request)

def about(request):
    return render(request, 
        template_name='library_collection/about.html',
        dictionary={
            'active_tab': active_tab(request),
            'current_path': request.path,
            'editing': editing(request.path),
        },
    )
