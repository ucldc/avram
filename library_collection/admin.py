# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from library_collection.models import (
    Campus, Repository, Collection, CollectionCustomFacet, HarvestTrigger,
    HarvestEvent, HarvestRun)
from library_collection.admin_actions import (
    set_ready_for_publication, export_as_csv, retrieve_solr_counts, 
    retrieve_metadata_density, set_for_rikolti_etl)
from library_collection.rikolti_actions import harvest_collection_set
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from rangefilter.filters import DateRangeFilter, NumericRangeFilter
from django_json_widget.widgets import JSONEditorWidget
from django.db import models

# Add is_active & date_joined to User admin list view
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name',
                          'is_active', 'date_joined', 'is_staff')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


def make_link(href, text, target='_self'):
    return mark_safe(f"<a href='{href}' target='{target}'>{text}</a>")


class HarvestEventAdmin(admin.ModelAdmin):
    list_display = (
        'display_status', 
        'event_str', 
        'display_date', 
        'harvest_run_link', 
        'event_airflow_link'
    )
    ordering=('-sns_timestamp',)
    list_display_links = ['event_str']

    @admin.display(description="Harvest Event", ordering="task_id")
    def event_str(self, instance):
        if not instance.collection:
            return f"{instance.harvest_run.dag_id}: {instance.task_display()}"
        return (
            f"{instance.collection.id}: {instance.harvest_run.dag_id}: "
            f"{instance.task_display()}"
        )

    @admin.display(description="Harvest Run")
    def harvest_run_link(self, instance):
        if not instance.collection:
            link_text = f"{instance.harvest_run.dag_id}"
        else:
            link_text = f"{instance.collection.id}: {instance.harvest_run.dag_id}"
        return make_link(instance.harvest_run.admin_url(), link_text)

    @admin.display(description="Event in Airflow")
    def event_airflow_link(self, instance):
        return make_link(instance.event_airflow_url(), 'Airflow Logs', '_blank')

    readonly_fields = [
        'collection_link',
        'harvest_run_link', 
        'task_id', 
        'try_number', 
        'map_index', 
        'verbose_status', 
        'display_date',
    ]

    @admin.display(description="Collection")
    def collection_link(self, instance):
        if instance.collection:
            return make_link(instance.collection.admin_url(), instance.collection)
        else:
            return '-'

    @admin.display(description="Status", ordering="error")
    def verbose_status(self, instance):
        box = instance.display_status()

        event_airflow = make_link(
            instance.event_airflow_url(), 'airflow', '_blank')
        description = (
            f"See 'rikolti message' below for "
            f"{'error' if instance.error else 'success'} information - "
            f"See event in {event_airflow}"
        )

        return mark_safe(f"{box} {description}")

    formfield_overrides = {
        models.TextField: {
            'widget': JSONEditorWidget(
                height='300px', 
                width='100%', 
                options={
                    'mode': 'view', 
                    'modes': ['view', 'preview'], 
                    'mainMenuBar': True, 
                    'navigationBar': False
                }
            )
        }
    }

    fieldsets = [
        (None, {"fields": readonly_fields + ['rikolti_message']}),
        ('SNS and SQS Details for Debugging', {
            "classes": ['collapse'],
            "fields": ['sqs_message', 'sns_message']
        })
    ]


class HarvestRunHarvestEventInline(admin.TabularInline):
    model = HarvestEvent
    readonly_fields = [
        'display_status', 
        'display_date', 
        'harvest_event_link', 
        'airflow_event_link'
    ]
    fields = tuple(readonly_fields)
    ordering = ('-sns_timestamp',)

    can_delete = False
    show_change_link = False
    extra = 0
    max_num = 0

    @admin.display(description="Harvest Event")
    def harvest_event_link(self, instance):
        return make_link(
            instance.admin_url(), f"{instance.task_display()}")

    def airflow_event_link(self, instance):
        return make_link(instance.event_airflow_url(), 'Airflow Logs', '_blank')


class HarvestRunAdmin(admin.ModelAdmin):
    inlines = [HarvestRunHarvestEventInline]

    list_display = (
        'display_status',
        'run_str',
        'display_date',
        'collection_link',
        'dag_run_airflow_link',
    )
    list_display_links = ['run_str']

    @admin.display(description="Harvest Run", ordering='dag_id')
    def run_str(self, instance):
        if instance.collection:
            return f"{instance.collection.id}: {instance.dag_id}"
        else:
            return f"{instance.dag_id}"

    @admin.display(ordering="collection__name", description="collection")
    def collection_link(self, instance):
        if instance.collection:
            return make_link(
                instance.collection.admin_url(), instance.collection.name)
        else:
            return '-'

    @admin.display(description="Airflow Dag Run Id", ordering="dag_run_id")
    def dag_run_airflow_link(self, instance):
        return make_link(
            instance.dag_run_airflow_url(), instance.dag_run_id, '_blank')

    readonly_fields = [
        'collection_link', 
        'dag_id', 
        'dag_run_airflow_link', 
        'utc_date', 
        'dag_run_conf',
        'harvest_trigger',
        'verbose_status'
    ]
    fields = tuple(readonly_fields) + ('status',)

    @admin.display(ordering='status', description="status")
    def verbose_status(self, instance):
        box = instance.display_status()
        event = instance.most_recent_event()

        event_link = make_link(
            event.admin_url(), f"{event.task_display()} {event.display_date}")
        event_airflow = make_link(
            event.event_airflow_url(), 'airflow', '_blank')

        description = (
            f"Most recent event: {event_link} - See event in {event_airflow}")
        return mark_safe(f"{box} {description}")


class CollectionHarvestRunInline(admin.TabularInline):
    model = HarvestRun

    fields = (
        'display_status', 
        'harvest_run_link', 
        'dag_run_airflow_link',
        'most_recent_event',
        'most_recent_event_datetime',
        'most_recent_event_logs',
    )
    readonly_fields = [
        'display_status', 
        'harvest_run_link', 
        'dag_run_airflow_link',
        'most_recent_event',
        'most_recent_event_datetime',
        'most_recent_event_logs',
    ]

    can_delete = False
    show_change_link = False
    extra = 0
    max_num = 0

    @admin.display(description="Harvest Run")
    def harvest_run_link(self, instance):
        return make_link(
            instance.admin_url(), f"{instance.dag_id}: {instance.display_date}")

    @admin.display(description="Airflow Dag Run Id", ordering="dag_run_id")
    def dag_run_airflow_link(self, instance):
        return make_link(
            instance.dag_run_airflow_url(), instance.dag_run_id, '_blank')

    @admin.display(description="Most Recent Event")
    def most_recent_event(self, instance):
        event = instance.most_recent_event()
        event_link = make_link(
            event.admin_url(), f"{event.task_display()} {event.display_date}"
        )
        return event_link

    @admin.display(description="Most Recent Event Time")
    def most_recent_event_datetime(self, instance):
        event = instance.most_recent_event()
        return event.display_date

    @admin.display(description="Most Recent Event Logs")
    def most_recent_event_logs(self, instance):
        event = instance.most_recent_event()
        return make_link(
            event.event_airflow_url(), 
            f"{event.task_display()} logs", 
            '_blank'
        )


class MerrittSetup(SimpleListFilter):
    title = 'Set up for Merritt'
    parameter_name = 'merritt'

    def lookups(self, request, model_admin):
        return (('MERRITT', 'Set up for Merritt'),('NOTMERRITT', 'Not set up for Merritt'))

    def queryset(self, request, queryset):
        if self.value() == 'MERRITT':
            return queryset.exclude(merritt_id='')
        if self.value() == 'NOTMERRITT':
            return queryset.filter(merritt_id='')


class NotInCampus(SimpleListFilter):
    title = 'Not on a Campus'
    parameter_name = 'nocampus'

    def lookups(self, request, model_admin):
        return (('NOCAMPUS', 'Not on a campus'), ('CAMPUS', 'on a campus'))

    def queryset(self, request, queryset):
        if self.value() == 'NOCAMPUS':
            return queryset.filter(campus=None)
        if self.value() == 'CAMPUS':
            return queryset.exclude(campus=None)


class URLFieldsListFilter(SimpleListFilter):
    '''Filter to find blank or filled URL fields'''
    title = 'URL Fields'
    lookup_table = {
        'LOCAL': ('has local URL', lambda x: x.exclude(url_local__exact='')),
        'LOCALNOT': ('missing local URL',
                     lambda x: x.filter(url_local__exact='')),
        'OAC': ('has OAC URL', lambda x: x.exclude(url_oac__exact='')),
        'OACNOT': ('missing OAC URL', lambda x: x.filter(url_oac__exact='')),
        'HARVEST': ('has HARVEST URL',
                    lambda x: x.exclude(url_harvest__exact='')),
        'HARVESTNOT': ('missing HARVEST URL',
                       lambda x: x.filter(url_harvest__exact='')),
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
        return tuple(
            [(k, v[0]) for k, v in URLFieldsListFilter.lookup_table.items()])

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


class HasDescriptionFilter(SimpleListFilter):
    title = 'Description'
    parameter_name = 'description'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Description provided'),
            ('false', 'No description')
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.exclude(description='')
        if self.value() == 'false':
            return queryset.filter(description='')


class SolrCountFilter(SimpleListFilter):
    title = 'Solr Count'
    parameter_name = 'solr_count'

    def lookups(self, request, model_admin):
        return (
            ('0', 'Empty'),
            ('1', 'Not Empty'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(solr_count__exact=0)
        if self.value() == '1':
            return queryset.filter(solr_count__gt=0)
        return queryset


# from: http://stackoverflow.com/questions/2805701/
class ActionInChangeFormMixin(object):
    def response_action(self, request, queryset):
        """
        Prefer http referer for redirect
        """
        response = super(ActionInChangeFormMixin, self).response_action(
            request, queryset)
        if isinstance(response, HttpResponseRedirect):
            response['Location'] = request.META.get('HTTP_REFERER',
                                                    request.path)
        return response

    def change_view(self, request, object_id, extra_context=None):
        actions = self.get_actions(request)
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(
                request)
        else:
            action_form = None
        return super(ActionInChangeFormMixin, self).change_view(
            request, object_id, extra_context={'action_form': action_form, })


class CollectionCustomFacetInline(admin.StackedInline):
    model = CollectionCustomFacet
    fk_name = 'collection'

class CollectionHarvestTriggerInline(admin.TabularInline):
    model = HarvestTrigger
    def airflow_link(self, instance):
        return mark_safe(
            f"<a href='{instance.dag_run_link}'>{instance.dag_run_id}</a>"
        )
    airflow_link.short_description = 'Airflow Link'

    fields = ('dag_run_id', 'airflow_execution_time', 'dag_id', 'airflow_link')
    readonly_fields = ['dag_run_id', 'airflow_execution_time', 'dag_id', 'airflow_link']
    can_delete = False
    show_change_link = True
    fk_name = 'collection'

class CollectionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CollectionAdminForm, self).__init__(*args, **kwargs)
        # self.fields['harvest_exception_notes'] = forms.CharField(
        #     widget=forms.Textarea(attrs={'readonly': 'readonly'})
        # )

    class Meta:
        model = Collection
        fields = '__all__'


class CollectionAdmin(ActionInChangeFormMixin, admin.ModelAdmin):
    # http://stackoverflow.com/a/11321942/1763984
    inlines = [
        CollectionCustomFacetInline, 
        CollectionHarvestTriggerInline, 
        CollectionHarvestRunInline
    ]
    form = CollectionAdminForm

    def campuses(self):
        return ", ".join([x.__str__() for x in self.campus.all()])
    campuses.short_description = "Campus"

    def repositories(self):
        return ", ".join([x.__str__() for x in self.repository.all()])
    repositories.short_description = "Repository"

    def numeric_key(self):
        return self.pk
    numeric_key.short_description = "Numeric key"
    numeric_key.admin_order_field = 'pk'

    def has_description(self):
        return bool(self.description)
    has_description.admin_order_field = 'description'

    def solr_count_str(self):
        return f'{self.solr_count:,}'
    solr_count_str.short_description = 'Solr Count'
    solr_count_str.admin_order_field = 'solr_count'

    def metadata_report_link(self):
        return mark_safe(
            f"<a href='https://calisphere.org/collections/"
            f"{self.id}/metadata'>metadata report</a>"
        )
    metadata_report_link.short_description = 'Metadata Report'

    def solr_last_updated(self):
        return self.solr_last_updated
    solr_last_updated.short_description = 'Solr-Registry Connection Last Updated'

    list_display = ('name', campuses, repositories,
                    numeric_key, 'date_last_harvested', has_description,
                    'mapper_type', 'rikolti_mapper_type',
                    solr_count_str, solr_last_updated,
                    metadata_report_link, 'metadata_density_score',
                    'metadata_density_score_last_updated')
    list_filter = [
        'campus', SolrCountFilter,
        ('solr_count', NumericRangeFilter), 'ready_for_publication',
        NotInCampus, 'harvest_type', URLFieldsListFilter, MerrittSetup,
        HasDescriptionFilter, 'mapper_type', 'rikolti_mapper_type',
        ('solr_last_updated', DateRangeFilter),
        'repository'
    ]
    save_on_top = True
    search_fields = ['name', 'description', 'enrichments_item']
    actions = [
        set_for_rikolti_etl,
        retrieve_solr_counts,
        export_as_csv,
        # queue_harvest_normal_stage,
        # queue_image_harvest_normal_stage,
        # queue_deep_harvest_normal_stage,
        # queue_deep_harvest_replace_normal_stage,
        # queue_sync_to_solr_normal_stage,
        # queue_sync_couchdb,
        # queue_sync_to_solr_normal_production,
        # queue_delete_couchdb_collection_stage,
        # queue_delete_from_solr_normal_stage,
        # queue_delete_couchdb_collection_production,
        # queue_delete_from_solr_normal_production,
        set_ready_for_publication,
        retrieve_metadata_density,
        harvest_collection_set,
    ]

    fieldsets = (
        (
            'Descriptive Information',
            {
                'fields': (
                    ('name', 'ready_for_publication'),
                    'campus',
                    'repository',
                    'description',
                    'local_id',
                    'url_local',
                    'url_oac',
                    'featured',
                    ('disqus_shortname_prod', 'disqus_shortname_test',)
                )
            },
        ), (
            'For Nuxeo Collections',
            {
                'fields': (('merritt_id', 'merritt_extra_data'),)
            }
        ), (
            'For Harvest Collections',
            {
                'fields': (
                    'harvest_type',
                    'url_harvest',
                    'harvest_extra_data',
                    'enrichments_item',
                    'date_last_harvested',
                    'harvest_exception_notes')
            }
        ), (
            'For enrichment chain',
            {
                'fields': (
                    'dcmi_type',
                    'rights_status',
                    'rights_statement',
                )
            }
        )
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "repository":
            kwargs["queryset"] = Repository.objects.order_by('name')
        return super(CollectionAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs)


class CampusAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

    def has_delete_permission(self, request, obj=None):
        return False


class RepositoryAdmin(admin.ModelAdmin):
    search_fields = ['name']

class HarvestTriggerAdmin(admin.ModelAdmin):
    def airflow_link(self):
        return mark_safe(
            f"<a href='{self.dag_run_link}'>{self.dag_run_id}</a>"
        )
    airflow_link.short_description = 'Airflow Link'

    list_display = ('collection', 'dag_run_id', airflow_link, 'dag_id')
    pass

admin.site.register(HarvestRun, HarvestRunAdmin)
admin.site.register(HarvestEvent, HarvestEventAdmin)
admin.site.register(HarvestTrigger, HarvestTriggerAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Campus, CampusAdmin)
admin.site.register(Repository, RepositoryAdmin)
# http://stackoverflow.com/questions/5742279/
# removing-sites-from-django-admin-page
try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass

# Copyright © 2016, Regents of the University of California
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of the University of California nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
