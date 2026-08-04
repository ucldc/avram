# urls.py
from django.conf.urls import include, url
from library_collection.models import Collection, Campus
from library_collection import views

from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib.sitemaps import GenericSitemap
from django.views.generic import TemplateView
from library_collection.api import v1_api

admin.autodiscover()

collection_dict = {
    'queryset': Collection.objects.all(),
}

campus_dict = {
    'queryset': Campus.objects.all(),
}

sitemaps = {
    "UC": GenericSitemap(campus_dict),
    "collection_registry": GenericSitemap(collection_dict),
}

urlpatterns = [
    url(r'^$', views.about, name='about'),
    url(r'^robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
    url(r'^api/', include(v1_api.urls)),
    url(r'^oai/', include('oai.urls', namespace="oai")),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/', LoginView.as_view(), name='login'),
    url(r'^sitemap\.xml$', sitemaps_views.sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    url(r'^edit/', include('library_collection.urls'), name='registry'),
]
