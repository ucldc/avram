from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from library_collection.feeds import AllFeed

from tastypie.api import Api
from library_collection.api import CollectionResource
from library_collection.api import CampusResource
from library_collection.api import RepositoryResource

v1_api = Api(api_name='v1')
v1_api.register(CollectionResource())
v1_api.register(CampusResource())
v1_api.register(RepositoryResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'library_collection.views.collections', name='collections'),
    url(r'^edit/$', 'library_collection.views.edit_collections', name='edit_collections'),
    url(r'rss$', AllFeed()),
    #url(r'',),
    url(r'^api/', include(v1_api.urls)),
    url(r'^edit/repositories/$', 'library_collection.views.edit_repositories', name='edit_repositories'),
    url(r'^edit/about/$', 'library_collection.views.edit_about', name='edit_about'),
    url(r'^edit/(?P<campus_slug>UC\w*)/repositories/$', 'library_collection.views.edit_repositories', name='edit_repositories'),
    url(r'^edit/(?P<campus_slug>UC.*)/$', 'library_collection.views.edit_collections', name='edit_collections'),
    url(r'^edit/(?P<colid>\d*)/(?P<col_slug>.*)/$', 'library_collection.views.edit_details', name='edit_detail'),
    url(r'^edit/(?P<colid>\d*)/$', 'library_collection.views.edit_details_by_id', name='edit_detail'),
    url(r'^repositories/$', 'library_collection.views.repositories', name='repositories'),
    url(r'^about/$', 'library_collection.views.about', name='about'),
    url(r'^(?P<campus_slug>UC.*)/repositories/$', 'library_collection.views.repositories', name='repositories'),
    url(r'^(?P<campus_slug>UC.*)/$', 'library_collection.views.collections', name='collections'),
    url(r'^(?P<colid>\d*)/(?P<col_slug>.*)/$', 'library_collection.views.details', name='detail'),
    url(r'^(?P<colid>\d*)/$', 'library_collection.views.details_by_id', name='detail'),
)
