# admin.py

from django.contrib import admin
from library_collection.models import *
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
import django.contrib.messages as messages


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
            'HARVEST': ('has HARVEST URL', lambda x: x.exclude(url_harvest__exact='')),
            'HARVESTNOT': ('missing HARVEST URL', lambda x: x.filter(url_harvest__exact='')),
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


def start_harvest_for_queryset(user, queryset):
    '''Start harvest for valid collections in the queryset'''
    success = False
    collections_to_harvest = [] 
    collections_invalid = []
    for collection in queryset:
        if collection.harvest_type == 'X' or not collection.url_harvest:
            collections_invalid.append(collection)
        else:
            collections_to_harvest.append(collection)
    cmd_line = ' '.join((collection.harvest_script, user.email))
    arg_coll_uri = ';'.join([c.url_api for c in collections_to_harvest])
    cmd_line = ' '.join((cmd_line, arg_coll_uri))
    try:
        p = subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        success = True
        msg = 'Started harvest for {} collections: {} CMD: {}'.format( len(collections_to_harvest), '  |  '.join([ c.name.encode('utf-8') for c in collections_to_harvest]), cmd_line)
    except OSError, e:
        if e.errno == 2:
            msg = 'Cannot find {} for harvesting {} collections {}'.format(
                    collection.harvest_script, len(collections_to_harvest),
                    '; '.join([c.name.encode('utf-8') for c in collections_to_harvest])
                    )
        else:
            msg = 'Error: Trying to run {} error-> {}'.format(cmd_line,
                    str(e)
                    )
    return msg, success, collections_invalid, collections_to_harvest

def start_harvest(modeladmin, request, queryset):
    msg, success, collections_invalid, collections_harvested = \
            start_harvest_for_queryset(request.user, queryset)
    if collections_invalid:
        msg_invalid = '{} collections not harvestable : {}'.format(
                len(collections_invalid), 
                '  |  '.join([c.name.encode('utf-8') for c in collections_invalid]))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
start_harvest.short_description = 'Start harvest for selected collections'

#from: http://stackoverflow.com/questions/2805701/
class ActionInChangeFormMixin(object):
    def response_action(self, request, queryset):
        """
        Prefer http referer for redirect
        """
        response = super(ActionInChangeFormMixin, self).response_action(request,
                queryset)
        if isinstance(response, HttpResponseRedirect):
            response['Location'] = request.META.get('HTTP_REFERER', request.path)
        return response  

    def change_view(self, request, object_id, extra_context=None):
        actions = self.get_actions(request)
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else: 
            action_form = None
        return super(ActionInChangeFormMixin, self).change_view(request, object_id, extra_context={
            'action_form': action_form,
        })

class CollectionAdmin(ActionInChangeFormMixin, admin.ModelAdmin):
    # http://stackoverflow.com/a/11321942/1763984
    def campuses(self):
        return ", " . join([x.__str__() for x in self.campus.all()])
    campuses.short_description = "Campus"
    def repositories(self):
        return ", " . join([x.__str__() for x in self.repository.all()])
    repositories.short_description = "Repository"

    list_display = ( 'name', campuses, repositories, 'human_extent', 'appendix', 'phase_one',)
    list_editable = ('appendix', 'phase_one')
    list_filter = [ 'campus', 'need_for_dams', 'appendix', 'harvest_type', URLFieldsListFilter]
    search_fields = ['name','description']
    actions = [ start_harvest, ]

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
try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass
admin.site.disable_action('delete_selected')
