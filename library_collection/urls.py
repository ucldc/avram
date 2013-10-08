from django.conf.urls import patterns, include, url
from library_collection.feeds import AllFeed

from tastypie.api import NamespacedApi
from library_collection.api import CollectionResource
from library_collection.api import CampusResource
from library_collection.api import RepositoryResource

#https://github.com/toastdriven/django-tastypie/issues/409
v1_api = NamespacedApi(api_name='v1', urlconf_namespace='registry')
v1_api.register(CollectionResource())
v1_api.register(CampusResource())
v1_api.register(RepositoryResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'library_collection.views.collections', name='collections'),
    url(r'rss$', AllFeed()),
    #url(r'',),
    url(r'^api/', include(v1_api.urls)),
    # Status/Format/Restriction/Need
    url(r'^repositories/$', 'library_collection.views.repositories', name='repositories'),
    url(r'^(?P<campus_slug>UC\w*)/repositories/$', 'library_collection.views.repositories', name='repositories'),
    url(r'^(?P<campus_slug>UC.*)/$', 'library_collection.views.collections', name='collections'),
    url(r'^(?P<colid>\d*)/(?P<col_slug>.*)/$', 'library_collection.views.details', name='detail'),
    url(r'^(?P<colid>\d*)/$', 'library_collection.views.details_by_id', name='detail'),
)
