# admin.py

from django.contrib import admin
from library_collections.models import *
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
 
class ProvenancialCollectionAdmin(admin.ModelAdmin):
    # http://stackoverflow.com/a/11321942/1763984
    def campuses(self):
        return ", " . join([x.__str__() for x in self.campus.all()])
    campuses.short_description = "Campus"

    list_display = ( 'name', campuses, 'human_extent', 'appendix', 'phase_one',)
    list_editable = ('appendix', 'phase_one')
    list_filter = [ 'campus', 'need_for_dams',]
    search_fields = ['name','description']

    def human_extent(self, obj):
        return obj.human_extent()
    human_extent.short_description = 'extent'

class CampusAdmin(admin.ModelAdmin):
    list_display = ('name','slug',)

admin.site.register(ProvenancialCollection, ProvenancialCollectionAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Status)
admin.site.register(Restriction)
#admin.site.register(Need)
# http://stackoverflow.com/questions/5742279/removing-sites-from-django-admin-page

admin.site.unregister(Group)
