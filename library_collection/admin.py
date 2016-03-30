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


def queue_harvest_for_queryset(user, queryset, rq_queue):
    '''Start harvest for valid collections in the queryset'''
    success = False
    collections_to_harvest = [] 
    collections_invalid = []
    for collection in queryset:
        if collection.harvest_type == 'X':
            collections_invalid.append((collection, 'Invalid harvest type'))
        elif not collection.url_harvest:
            collections_invalid.append((collection, 'No harvest URL'))
        elif 'prod' in rq_queue and not collection.ready_for_publication:
            collections_invalid.append((collection,
             'Not ready for production. Check "ready for publication" to harvest to production'))
        else:
            collections_to_harvest.append(collection)
    cmd_line = ' '.join((collection.harvest_script, user.email, rq_queue))
    arg_coll_uri = ';'.join([c.url_api for c in collections_to_harvest])
    cmd_line = ' '.join((cmd_line, arg_coll_uri))
    try:
        p = subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        success = True
        msg = 'Queued harvest for {} collections: {} CMD: {}'.format( len(collections_to_harvest), '  |  '.join([ c.name.encode('utf-8') for c in collections_to_harvest]), cmd_line)
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

def queue_harvest(modeladmin, request, queryset, rq_queue):
    msg, success, collections_invalid, collections_harvested = \
            queue_harvest_for_queryset(request.user, queryset, rq_queue)
    if collections_invalid:
        msg_invalid = '{} collections not harvestable. '.format(
                len(collections_invalid)) 
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid,
                '#{} {} - {}; '.format(coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)

def queue_harvest_normal_stage(modeladmin, request, queryset):
    return queue_harvest(modeladmin, request, queryset, 'normal-stage')
queue_harvest_normal_stage.short_description = ''.join(('Queue harvest for ',
                'collection(s) on normal queue'))

def queue_harvest_high_stage(modeladmin, request, queryset):
    return queue_harvest(modeladmin, request, queryset, 'high-stage')
queue_harvest_high_stage.short_description = ''.join(('Queue harvest for ',
                'collection(s) on high queue'))

def queue_image_harvest_for_queryset(user, queryset, rq_queue):
    '''Start harvest for valid collections in the queryset'''
    success = False
    collections_to_harvest = [] 
    collections_invalid = []
    for collection in queryset:
        if 'prod' in rq_queue and not collection.ready_for_publication:
            collections_invalid.append((collection,
             'Not ready for production. Check "ready for publication" to harvest to production'))
        else:
            collections_to_harvest.append(collection)
    cmd_line = ' '.join((collection.image_harvest_script, user.email, rq_queue))
    arg_coll_uri = ';'.join([c.url_api for c in collections_to_harvest])
    cmd_line = ' '.join((cmd_line, arg_coll_uri))
    try:
        p = subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        success = True
        msg = 'Queued image harvest for {} collections: {} CMD: {}'.format( len(collections_to_harvest), '  |  '.join([ c.name.encode('utf-8') for c in collections_to_harvest]), cmd_line)
    except OSError, e:
        if e.errno == 2:
            msg = 'Cannot find {} for image harvesting {} collections {}'.format(
                    collection.image_harvest_script, len(collections_to_harvest),
                    '; '.join([c.name.encode('utf-8') for c in collections_to_harvest])
                    )
        else:
            msg = 'Error: Trying to run {} error-> {}'.format(cmd_line,
                    str(e)
                    )
    return msg, success, collections_invalid, collections_to_harvest

def queue_image_harvest(modeladmin, request, queryset, rq_queue):
    msg, success, collections_invalid, collections_harvested = \
            queue_image_harvest_for_queryset(request.user, queryset, rq_queue)
    if collections_invalid:
        msg_invalid = '{} collections not harvestable. '.format(
                len(collections_invalid)) 
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid,
                '#{} {} - {}; '.format(coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)

def queue_image_harvest_normal_stage(modeladmin, request, queryset):
    return queue_image_harvest(modeladmin, request, queryset, 'normal-stage')
queue_image_harvest_normal_stage.short_description = ''.join(('Queue image ',
                'harvest for collection(s) on normal queue'))

def queue_image_harvest_high_stage(modeladmin, request, queryset):
    return queue_image_harvest(modeladmin, request, queryset, 'high-stage')
queue_image_harvest_high_stage.short_description = ''.join(('Queue image ',
                'harvest for collection(s) on high queue'))

def queue_sync_couchdb_for_queryset(user, queryset):
    '''Sync couchdb to production for valid collections in the queryset'''
    success = False
    collections_to_harvest = []
    collections_success = []
    collections_invalid = []
    msg = ''
    for collection in queryset:
        if not collection.ready_for_publication:
            collections_invalid.append((collection,
             'Not ready for production. Check "ready for publication" to sync to production'))
        else:
            collections_to_harvest.append(collection)
    for collection in collections_to_harvest:
        cmd_line = collection.sync_couchdb_script
        cmd_line = ' '.join((cmd_line, str(collection.id)))
        try:
            p = subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
            success = True
            collections_success.append(collection)
        except OSError, e:
            if e.errno == 2:
                msg += 'Cannot find {} for syncing {} collections {}'.format(
                        collection.sync_couchdb_script, len(collections_to_harvest),
                        '; '.join([c.name.encode('utf-8') for c in collections_to_harvest])
                        )
            else:
                msg += 'Error: Trying to run {} error-> {}'.format(cmd_line,
                        str(e)
                        )
    if len(collections_success):
        msg += 'Queued sync couchdb for {} collections: {} CMD: {}'.format( len(collections_success), '  |  '.join([ c.name.encode('utf-8') for c in collections_success]), cmd_line)
    return msg, success, collections_invalid, collections_success

def queue_sync_couchdb(modeladmin, request, queryset):
    msg, success, collections_invalid, collections_harvested = \
            queue_sync_couchdb_for_queryset(request.user, queryset)
    if collections_invalid:
        msg_invalid = '{} collections not syncable. '.format(
                len(collections_invalid)) 
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid,
                '#{} {} - {}; '.format(coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
queue_sync_couchdb.short_description = ''.join(('Queue sync to production ',
                'couchdb for collection(s)'))

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

    def numeric_key(self):
        return self.pk
    numeric_key.short_description = "Numeric key"

    list_display = ( 'name', campuses, repositories, 'human_extent', 
                     numeric_key )
    list_filter = [ 'campus', 'ready_for_publication', 'harvest_type', URLFieldsListFilter, 'repository']
    search_fields = ['name','description']
    actions = [ queue_harvest_normal_stage, queue_harvest_high_stage,
                queue_image_harvest_normal_stage,
                queue_image_harvest_high_stage,
                queue_sync_couchdb
                ]
    fieldsets = (
            ('Descriptive Information', {
                'fields': ('name', 'campus', 'repository', 'description',
                    'local_id', 'url_local', 'url_oac', 'rights_status',
                    'rights_statement', 'ready_for_publication',
                    'featured')
                },
                ),
            ('For Nuxeo Collections', {
                #'classes': ('collapse',),
                'fields': ('extent', 'formats', 'hosted', 'staging_notes',
                        'files_in_hand', 'files_in_dams',
                        'metadata_in_dams', 'qa_completed',)
                }
                ),
            ('For Harvest Collections', {
                'fields': ('harvest_type', 'dcmi_type', 'url_harvest',
                    'harvest_extra_data', 'enrichments_item'),
                }
                )
            )

    def human_extent(self, obj):
        return obj.human_extent
    human_extent.short_description = 'extent'

class CampusAdmin(admin.ModelAdmin):
    list_display = ('name','slug',)

admin.site.register(Collection, CollectionAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Repository)
# http://stackoverflow.com/questions/5742279/removing-sites-from-django-admin-page
try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass
admin.site.disable_action('delete_selected')
