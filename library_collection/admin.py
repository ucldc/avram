# admin.py

from django.contrib import admin
from library_collection.models import *
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.admin import SimpleListFilter

class URLFieldsListFilter(SimpleListFilter):
    '''Filter to find blank or filled URL fields'''
    title = 'URL Fields'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'urlfields'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('LOCAL', 'has local URL'),
            ('LOCALNOT', 'missing local URL'),
            ('OAC', 'has OAC URL'),
            ('OACNOT', 'missing OAC URL'),
            ('OAI', 'has OAI URL'),
            ('OAINOT', 'missing OAI URL'),
            ('WAS', 'has WAS URL'),
            ('WASNOT', 'missing WAS URL'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'LOCAL':
            return queryset.exclude(url_local__exact='')
        if self.value() == 'LOCALNOT':
            return queryset.filter(url_local__exact='')
        if self.value() == 'OAC':
            return queryset.exclude(url_oac__exact='')
        if self.value() == 'OACNOT':
            return queryset.filter(url_oac__exact='')
        if self.value() == 'OAI':
            return queryset.exclude(url_oai__exact='')
        if self.value() == 'OAINOT':
            return queryset.filter(url_oai__exact='')
        if self.value() == 'WAS':
            return queryset.exclude(url_was__exact='')
        if self.value() == 'WASNOT':
            return queryset.filter(url_was__exact='')
 

class ProvenancialCollectionAdmin(admin.ModelAdmin):
    # http://stackoverflow.com/a/11321942/1763984
    def campuses(self):
        return ", " . join([x.__str__() for x in self.campus.all()])
    campuses.short_description = "Campus"

    list_display = ( 'name', campuses, 'human_extent', 'appendix', 'phase_one',)
    list_editable = ('appendix', 'phase_one')
    list_filter = [ 'campus', 'need_for_dams', URLFieldsListFilter]
    search_fields = ['name','description']

    def human_extent(self, obj):
        return obj.human_extent
    human_extent.short_description = 'extent'

class CampusAdmin(admin.ModelAdmin):
    list_display = ('name','slug',)

admin.site.register(ProvenancialCollection, ProvenancialCollectionAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Status)
admin.site.register(Restriction)
#admin.site.register(Need)
# http://stackoverflow.com/questions/5742279/removing-sites-from-django-admin-page
admin.site.unregister(Site)
admin.site.disable_action('delete_selected')

