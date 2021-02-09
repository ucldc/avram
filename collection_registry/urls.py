# urls.py
from django.conf.urls import include, url
from library_collection.models import Collection, Campus

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps import views as sitemaps_views
# from ajax_select import urls as ajax_select_urls
from django.contrib.sitemaps import GenericSitemap
# http://stackoverflow.com/questions/11428427/no-module-named-simple-error-in-django
# from django.views.generic.simple import redirect_to
#from some_app.views import AboutView
from django.views.generic import TemplateView
from exhibits.views import calCultures

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
    url(r'^robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
    url(r'^exhibitions/', include('exhibits.urls', namespace="exhibits")),
    url(r'^for-educators/', include(('exhibits.teacher_urls', 'for-teachers'), namespace="for-teachers")),
    url(r'^cal-cultures/', calCultures, name="cal-cultures"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/', auth_views.login, name='login'),
    url(r'^sitemap\.xml$', sitemaps_views.sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    url(r'^', include('library_collection.urls'), name='registry'),
]
