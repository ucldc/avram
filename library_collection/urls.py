from django.conf.urls import include, url
from django.views.generic import TemplateView
from library_collection.feeds import AllFeed
from library_collection import views

from tastypie.api import Api
from library_collection.api import CollectionResource
from library_collection.api import CampusResource
from library_collection.api import RepositoryResource
from library_collection.api import RikoltiCollectionResource
from library_collection.api import RikoltiFetcherResource
from library_collection.api import RikoltiMapperResource

v1_api = Api(api_name='v1')
v1_api.register(CollectionResource())
v1_api.register(CampusResource())
v1_api.register(RepositoryResource())
v1_api.register(RikoltiCollectionResource())
v1_api.register(RikoltiFetcherResource())
v1_api.register(RikoltiMapperResource())

urlpatterns = [
    # Examples:
    url(r'^$', views.collections, name='collections'),
    url(r'^edit/$', views.edit_collections, name='edit_collections'),
    url(r'rss$', AllFeed()),
    #url(r'',),
    url(r'^api/', include(v1_api.urls)),
    url(r'^edit/repositories/$', views.edit_repositories, name='edit_repositories'),
    url(r'^edit/about/$', views.edit_about, name='edit_about'),
    url(r'^edit/(?P<campus_slug>UC\w*)/repositories/$', views.edit_repositories, name='edit_repositories'),
    url(r'^edit/(?P<campus_slug>UC.*)/$', views.edit_collections, name='edit_collections'),
    url(r'^edit/(?P<colid>\d*)/(?P<col_slug>.*)/$', views.edit_details, name='edit_detail'),
    url(r'^edit/(?P<colid>\d*)/$', views.edit_details_by_id, name='edit_detail'),
    url(r'^repositories/$', views.repositories, name='repositories'),
    # url(r'^repositories/(?P<repository_slug>', views.repositories, name='repositories'),
    url(r'^about/$', views.about, name='about'),
    url(r'^(?P<campus_slug>UC.*)/repositories/$', views.repositories, name='repositories'),
    url(r'^(?P<campus_slug>UC.*)/$', views.collections, name='collections'),
    url(r'^(?P<colid>\d*)/(?P<col_slug>.*)/$', views.details, name='detail'),
    url(r'^(?P<colid>\d*)/$', views.details_by_id, name='detail'),
    url(r'^repository/(?P<repoid>\d*)/$', views.repository_by_id, name='repository_collections'),
    url(r'^repository/(?P<repoid>\d*)/(?P<repo_slug>.*)/$', views.repository_collections, name='repository_collections'),
]
