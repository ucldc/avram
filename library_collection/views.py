# views.py

import operator
from django.shortcuts import render
from django.http import Http404
from library_collection.models import Collection, Campus, Repository
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from human_to_bytes import bytes2human
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from library_collection.decorators import verification_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import QueryDict

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
                'new': 'true',
            }
            if error:
                context['error'] = error
                
                collection = {'name': requestObj['name']}
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
                new_collection = Collection(name=requestObj['name'], )
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

def _get_direct_navigate_page_links(get_qd, page_number, num_pages, total_displayed=6):
    '''Return the ranges for the "before" and "after" direct page links.
    Also, return the previous/next group start links.
    Preserve any other information in the GET querydict as well.
    want to build a list of 5-7 pages around the current page, 3 each side?
    num_links indicates total number of additional links to create, if possible
    '''
    half = total_displayed / 2
    if page_number - half <= 0: #lower boundary
        lowest_page_number = 1
        num_high = total_displayed - page_number
        hnum = page_number + num_high + 2
        highest_page_number = hnum if hnum < num_pages else num_pages
    elif page_number + half > num_pages: # upper boundary
        highest_page_number = num_pages
        num_low = page_number + total_displayed - num_pages
        lnum = page_number - num_low
        lowest_page_number = lnum if lnum > 0 else 1
    else: #ok just halve them
        lowest_page_number = page_number - half
        highest_page_number = page_number + half + 1
    previous_page_qs = []
    next_page_qs = []
    for x in range(lowest_page_number, page_number):
        get_qd['page'] = x
        previous_page_qs.append((x, get_qd.urlencode()))
    #previous_page_numbers = [get_qd.update('page') = x for x in range(lowest_page_number, page_number)]
    previous_group_start_num = lowest_page_number -1 if (lowest_page_number -1) > 1 else 1
    get_qd['page'] = previous_group_start_num
    previous_group_start = get_qd.urlencode()
    for x in range(page_number+1, highest_page_number):
        get_qd['page'] = x
        next_page_qs.append((x, get_qd.urlencode()))

    next_group_start_num = highest_page_number  if highest_page_number  < num_pages else num_pages
    get_qd['page'] = next_group_start_num 
    next_group_start = get_qd.urlencode()
    return previous_page_qs, next_page_qs, previous_group_start, next_group_start

# collections in a repository
def repository_collections(request, repoid=None, repo_slug=None):
    repository = get_object_or_404(Repository, pk=repoid)
    # repository = Repository.objects.get(ark=repoark)
    collections = Collection.objects.filter(~Q(harvest_type='X'), repository=repository.id).order_by('name')
    page = request.GET.get('page')

    harvest_type = request.GET.get('harvest_type', '')

    harvest_types = ['OAC', 'NUX', 'OAI', 'SLR', 'MRC', 'TBD', '' ]
    if not harvest_type in harvest_types:
        raise Http404

    if harvest_type:
        collections = collections.filter(Q(harvest_type=harvest_type))

    paginator = Paginator(collections, 25) #get from url param?

    harvest_types = Collection.HARVEST_TYPE_CHOICES

    try:
        collections_for_page = paginator.page(page)
    except PageNotAnInteger:
        collections_for_page = paginator.page(1)
    except EmptyPage:
        collections_for_page = paginator.page(paginator.num_pages)
    page_number = collections_for_page.number
    qd = request.GET.copy()
    qd['page'] = page_number
    num_pages = paginator.num_pages
    previous_page_links, next_page_links, previous_group_start, next_group_start = _get_direct_navigate_page_links(qd, page_number, num_pages, 6)
    qd['page'] = 1
    first_page_qs = qd.urlencode()
    qd['page'] = num_pages
    last_page_qs = qd.urlencode()
    return render(request,
        template_name='library_collection/repository_collection_list.html',
        dictionary = { 
            'collections': collections_for_page, 
            'repository': repository,
            'repositories': repository,
            'campuses': campuses, 
            'active_tab': active_tab(request),
            'current_path': request.path,
            'editing': editing(request.path),
            'previous_page_links': previous_page_links,
            'previous_group_start': previous_group_start,
            'next_page_links': next_page_links,
            'next_group_start': next_group_start,
            'first_page_qs': first_page_qs,
            'last_page_qs': last_page_qs,
            #'query': query,
            'harvest_types': harvest_types,
            'harvest_type': harvest_type,
        },
    )

# view of collections in list. Currently home page
def collections(request, campus_slug=None):
    campus = None
    query = request.GET.get('q', '')
    search = None
    harvest_type = request.GET.get('harvest_type', '')

    harvest_types = ['OAC', 'NUX', 'OAI', 'SLR', 'MRC', 'TBD', '' ]
    if not harvest_type in harvest_types:
        raise Http404


    harvest_types = Collection.HARVEST_TYPE_CHOICES

    # turn input query into search for later filtering
    if query:
        if query.startswith('^'):
            search = (Q(name__istartswith=query[1:]), Q(url_oac__startswith=query[1:]))
        elif query.startswith('='):
            search = (Q(name__exact=query[1:]), Q(url_oac__exact=query[1:]))
        elif query.startswith('@'):
            search = (Q(name__search=query[1:]), Q(url_oac__search=query[1:]))
        else:
            search = (Q(name__icontains=query), Q(url_oac__icontains=query))

    # apply campus limits, by default excluding unknow harvest type 'X' (~Q is negative query)
    if campus_slug:
        if campus_slug == 'UC-':
            campus = None
            collections = Collection.objects.filter(~Q(harvest_type='X'), campus=None).order_by('name')
        else:
            campus = get_object_or_404(Campus, slug=campus_slug)
            collections = Collection.objects.filter(~Q(harvest_type='X'), campus__slug__exact=campus.slug).order_by('name').prefetch_related('campus')
    else:
        collections = Collection.objects.filter(~Q(harvest_type='X')).order_by('name').prefetch_related('campus')

    if harvest_type:
        collections = collections.filter(Q(harvest_type=harvest_type))

    # if query yielded a search, filter
    if search:
        collections = collections.filter(reduce(operator.or_, search)).prefetch_related('campus')

    paginator = Paginator(collections, 25) #get from url param?
    page = request.GET.get('page')
    try:
        collections_for_page = paginator.page(page)
    except PageNotAnInteger:
        collections_for_page = paginator.page(1)
    except EmptyPage:
        collections_for_page = paginator.page(paginator.num_pages)
    page_number = collections_for_page.number
    qd = request.GET.copy()
    qd['page'] = page_number
    num_pages = paginator.num_pages
    previous_page_links, next_page_links, previous_group_start, next_group_start = _get_direct_navigate_page_links(qd, page_number, num_pages, 6)
    qd['page'] = 1
    first_page_qs = qd.urlencode()
    qd['page'] = num_pages
    last_page_qs = qd.urlencode()
    return render(request,
        template_name='library_collection/collection_list.html',
        dictionary = { 
            'collections': collections_for_page, 
            'campus': campus,
            'campuses': campuses, 
            'active_tab': active_tab(request),
            'current_path': request.path,
            'editing': editing(request.path),
            'previous_page_links': previous_page_links,
            'previous_group_start': previous_group_start,
            'next_page_links': next_page_links,
            'next_group_start': next_group_start,
            'first_page_qs': first_page_qs,
            'last_page_qs': last_page_qs,
            'query': query,
            'harvest_types': harvest_types,
            'harvest_type': harvest_type,
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
                context['harvestTypeChoices'] = Collection.HARVEST_TYPE_CHOICES
                context['edit'] = 'true'
                
                if error:
                    context['error'] = error
                    collection.name = requestObj['name']
                    collection.campus = requestObj.getlist('campuses')
                    collection.repository = requestObj.getlist('repositories')
                    
                    if requestObj['name'] == '':
                        context['error'] = "Please enter a collection title"
                    
                    context['collection'] = collection
                
                return render(request,
                    template_name='library_collection/collection_edit.html',
                    dictionary=context
                )
            else: 
                collection.name = requestObj.get("name")
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

def repository_by_id(request, repoid):
    repository = get_object_or_404(Repository, pk=repoid)
    return redirect(repository, permanent=True)

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
        if campus_slug == 'UC-':
            campus = None
            repositories = Repository.objects.filter(campus=None).order_by('name').prefetch_related('campus')
        else:
            campus = get_object_or_404(Campus, slug=campus_slug)
            repositories = Repository.objects.filter(campus=campus).order_by('name').prefetch_related('campus')
    else:
        repositories = Repository.objects.all().order_by('name').prefetch_related('campus')
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
