# -*- coding: utf-8 -*-
import datetime
from django.contrib import admin
from django import forms
from library_collection.duration_widget import MultiValueDurationField
from library_collection.models import Campus, Repository, \
    Collection, CollectionCustomFacet
from library_collection.admin_actions import queue_harvest_normal_stage, \
    queue_image_harvest_normal_stage, queue_sync_couchdb, \
    set_ready_for_publication, queue_delete_from_solr_normal_production, \
    queue_sync_to_solr_normal_production, queue_sync_to_solr_normal_stage, \
    queue_deep_harvest_normal_stage, queue_delete_from_solr_normal_stage, \
    queue_deep_harvest_replace_normal_stage, \
    queue_delete_couchdb_collection_stage, \
    queue_delete_couchdb_collection_production, export_as_csv, \
    retrieve_solr_counts, retrieve_metadata_density, set_for_rikolti_etl
from django.contrib.sites.models import Site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.db.models import F
from rangefilter.filters import DateRangeFilter, NumericRangeFilter

# Add is_active & date_joined to User admin list view
UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name',
                          'is_active', 'date_joined', 'is_staff')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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
    inlines = [CollectionCustomFacetInline, ]
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
        return (
            f"<a href='https://calisphere.org/collections/"
            f"{self.id}/metadata'>metadata report</a>"
        )
    metadata_report_link.short_description = 'Metadata Report'
    metadata_report_link.allow_tags = True

    def solr_last_updated(self):
        print(self.solr_last_updated)
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
        queue_harvest_normal_stage,
        queue_image_harvest_normal_stage,
        queue_deep_harvest_normal_stage,
        queue_deep_harvest_replace_normal_stage,
        queue_sync_to_solr_normal_stage,
        queue_sync_couchdb,
        queue_sync_to_solr_normal_production,
        queue_delete_couchdb_collection_stage,
        queue_delete_from_solr_normal_stage,
        queue_delete_couchdb_collection_production,
        queue_delete_from_solr_normal_production,
        set_ready_for_publication,
        retrieve_metadata_density
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

    def has_delete_permission(self, request, obj=None):
        return False


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
