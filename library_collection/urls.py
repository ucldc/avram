from django.conf.urls import url
from library_collection import views

urlpatterns = [
    url(r'^collections/$', views.edit_collections, name='collections'),
    url(r'^repositories/$', views.edit_repositories, name='repositories'),
    url(r'^(?P<campus_slug>UC.*)/repositories/$', views.edit_repositories, name='repositories'),
    url(r'^(?P<campus_slug>UC.*)/$', views.edit_collections, name='collections'),
    url(r'^(?P<colid>\d*)$', views.edit_details, name='detail'),
    url(r'^(?P<colid>\d*)/(?P<col_slug>.*)$', views.edit_details, name='detail'),
    url(r'^repository/(?P<repoid>\d*)/$', views.repository_by_id, name='repository_collections'),
    url(r'^repository/(?P<repoid>\d*)/(?P<repo_slug>.*)/$', views.repository_collections, name='repository_collections'),
]
