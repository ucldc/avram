from django.conf.urls import patterns, include, url
from library_collection.feeds import AllFeed

from tastypie.api import Api
from library_collection.api import ProvenancialCollectionResource
from library_collection.api import CampusResource

v1_api = Api(api_name='v1')
v1_api.register(ProvenancialCollectionResource())
v1_api.register(CampusResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'library_collection.views.home', name='home'),
    url(r'rss$', AllFeed()),
    #url(r'',),
    url(r'^api/', include(v1_api.urls)),
    # Status/Format/Restriction/Need
    url(r'^(UC.*)/$', 'library_collection.views.UC', name='UC'),
    #url(r'^(UC.*)/(Status)/(.*)$', 'library_collection.views.UClimit', name='UClimit'),
    #url(r'^(UC.*)/(Format)/(.*)$', 'library_collection.views.UClimit', name='UClimit'),
    #url(r'^(UC.*)/(Restriction)/(.*)$', 'library_collection.views.UClimit', name='UClimit'),
    #url(r'^(UC.*)/(Need)/(.*)$', 'library_collection.views.UClimit', name='UClimit'),
    #url(r'^(?P<slug>.*)$', 'library_collection.views.details', name='detail'),
    url(r'^(\d*)/(.*)/$', 'library_collection.views.details', name='detail'),
    url(r'^(\d*)/$', 'library_collection.views.details_by_id', name='detail'),
)
