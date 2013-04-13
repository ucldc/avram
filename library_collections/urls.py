from django.conf.urls import patterns, include, url
from library_collections.feeds import AllFeed

from tastypie.api import Api
from library_collections.api import ProvenancialCollectionResource

v1_api = Api(api_name='v1')
v1_api.register(ProvenancialCollectionResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'library_collections.views.home', name='home'),
    url(r'rss$', AllFeed()),
    #url(r'',),
    url(r'^api/', include(v1_api.urls)),
    # Status/Format/Restriction/Need
    url(r'^(UC.*)/$', 'library_collections.views.UC', name='UC'),
    #url(r'^(UC.*)/(Status)/(.*)$', 'library_collections.views.UClimit', name='UClimit'),
    #url(r'^(UC.*)/(Format)/(.*)$', 'library_collections.views.UClimit', name='UClimit'),
    #url(r'^(UC.*)/(Restriction)/(.*)$', 'library_collections.views.UClimit', name='UClimit'),
    #url(r'^(UC.*)/(Need)/(.*)$', 'library_collections.views.UClimit', name='UClimit'),
    #url(r'^(?P<slug>.*)$', 'library_collections.views.details', name='detail'),
    url(r'^(\d*)/(.*)/$', 'library_collections.views.details', name='detail'),
    url(r'^(\d*)/$', 'library_collections.views.details_by_id', name='detail'),
)
