# admin.py

from django.contrib import admin
from library_collection.models import *
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.admin import SimpleListFilter


#Add is_active & date_joined to User admin list view
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class URLFieldsListFilter(SimpleListFilter):
    '''Filter to find blank or filled URL fields'''
    title = 'URL Fields'
    lookup_table = {
            'LOCAL': ('has local URL', lambda x: x.exclude(url_local__exact='')),
            'LOCALNOT': ('missing local URL', lambda x: x.filter(url_local__exact='')),
            'OAC': ('has OAC URL', lambda x: x.exclude(url_oac__exact='')),
            'OACNOT': ('missing OAC URL', lambda x: x.filter(url_oac__exact='')),
            'OAI': ('has OAI URL', lambda x: x.exclude(url_oai__exact='')),
            'OAINOT': ('missing OAI URL', lambda x: x.filter(url_oai__exact='')),
            'WAS': ('has WAS URL', lambda x: x.exclude(url_was__exact='')),
            'WASNOT': ('missing WAS URL', lambda x: x.filter(url_was__exact='')),
            }

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
        return tuple([ (k, v[0]) for k,v in URLFieldsListFilter.lookup_table.items()])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        try:
            return URLFieldsListFilter.lookup_table[self.value()][1](queryset)
        except KeyError:
            pass


class CollectionAdmin(admin.ModelAdmin):
    # http://stackoverflow.com/a/11321942/1763984
    def campuses(self):
        return ", " . join([x.__str__() for x in self.campus.all()])
    campuses.short_description = "Campus"
    def repositories(self):
        return ", " . join([x.__str__() for x in self.repository.all()])
    repositories.short_description = "Repository"

    list_display = ( 'name', campuses, repositories, 'human_extent', 'appendix', 'phase_one',)
    list_editable = ('appendix', 'phase_one')
    list_filter = [ 'campus', 'need_for_dams', 'appendix', URLFieldsListFilter]
    search_fields = ['name','description']

    def human_extent(self, obj):
        return obj.human_extent
    human_extent.short_description = 'extent'

class CampusAdmin(admin.ModelAdmin):
    list_display = ('name','slug',)

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Repository)
admin.site.register(Status)
admin.site.register(Restriction)
#admin.site.register(Need)
# http://stackoverflow.com/questions/5742279/removing-sites-from-django-admin-page
admin.site.unregister(Site)
admin.site.disable_action('delete_selected')
