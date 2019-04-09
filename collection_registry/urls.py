# urls.py
from django.conf.urls import patterns, include, url
from library_collection.models import Collection, Campus

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemaps_views
# from ajax_select import urls as ajax_select_urls
from django.contrib.sitemaps import GenericSitemap
# http://stackoverflow.com/questions/11428427/no-module-named-simple-error-in-django
# from django.views.generic.simple import redirect_to
from django.conf.urls import patterns, url, include
#from some_app.views import AboutView


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
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/', auth_views.login),
    url(r'^sitemap\.xml$', sitemaps_views.sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    url(r'^', include('library_collection.urls'), name='registry'),
]
