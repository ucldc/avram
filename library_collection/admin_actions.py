# -*- coding: utf-8 -*-
import os
import subprocess
import shlex
import csv
import django.contrib.messages as messages
from django.http import HttpResponse
from django.utils import timezone
from exhibits.cache_retry import SOLR_select

HARVEST_SCRIPT = os.environ.get('HARVEST_SCRIPT', os.environ['HOME'] +
                                '/code/harvester/queue_harvest.sh')
IMAGE_HARVEST_SCRIPT = os.environ.get(
        'IMAGE_HARVEST_SCRIPT',
        os.environ['HOME'] + '/code/harvester/queue_image_harvest.sh')
SYNC_COUCHDB_SCRIPT = os.environ.get(
        'SYNC_COUCHDB_SCRIPT',
        os.environ['HOME'] + '/code/harvester/queue_sync_couchdb.sh')
SYNC_TO_SOLR_SCRIPT = os.environ.get(
        'SYNC_TO_SOLR_SCRIPT',
        os.environ['HOME'] + '/code/harvester/queue_sync_to_solr.sh')
DELETE_FROM_SOLR_SCRIPT = os.environ.get(
        'SYNC_TO_SOLR_SCRIPT',
        os.environ['HOME'] +
        '/code/harvester/queue_delete_solr_collection.sh')
DEEP_HARVEST_SCRIPT = os.environ.get(
        'DEEP_HARVEST_SCRIPT',
        os.environ['HOME'] +
        '/code/harvester/queue_deep_harvest.sh')
DEEP_HARVEST_SCRIPT_REPLACE = '{} --replace '.format(DEEP_HARVEST_SCRIPT)
DELETE_COUCHDB_SCRIPT = os.environ.get(
        'DELETE_COUCHDB_SCRIPT',
        os.environ['HOME'] +
        '/code/harvester/queue_delete_couchdb_collection.sh')


def run_script_for_queryset(script,
                            queryset,
                            rq_queue,
                            collection_attr='id',
                            user={'email': 'example@example.edu'}):
    success = False
    collection_args_list = ';'.join(
            [str(getattr(c, collection_attr)) for c in queryset])
    cmd_line = ' '.join((script, user.email, rq_queue))
    cmd_line = ' '.join((cmd_line, collection_args_list))
    try:
        subprocess.Popen(shlex.split(cmd_line))
        success = True
        msg = 'Queued {} for {} collections: {} CMD: {}'.format(
                script,
                len(queryset),
                '  |  '.join(
                    [c.name for c in queryset]),
                cmd_line)
    except OSError as e:
        if e.errno == 2:
            msg = 'Cannot find {} for running {} collections {}'.format(
                script,
                len(queryset), '; '.join(
                    [c.name for c in queryset]))
        else:
            msg = 'Error: Trying to run {} error-> {}'.format(cmd_line, str(e))
    return msg, success


def queue_harvest(modeladmin, request, queryset, rq_queue):
    collections_to_harvest = []
    collections_invalid = []
    for collection in queryset:
        if collection.harvest_type == 'X':
            collections_invalid.append((collection, 'Invalid harvest type'))
        elif not collection.url_harvest:
            collections_invalid.append((collection, 'No harvest URL'))
        elif 'prod' in rq_queue and not collection.ready_for_publication:
            collections_invalid.append((collection,
                                        'Not ready for production. Check '
                                        '"ready for publication" to harvest '
                                        'to production'))
        else:
            collections_to_harvest.append(collection)
    msg, success = run_script_for_queryset(
            HARVEST_SCRIPT,
            collections_to_harvest,
            rq_queue,
            collection_attr='url_api',
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not harvestable. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid, '#{} {} - {}; '.format(
                coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


def queue_harvest_normal_stage(modeladmin, request, queryset):
    return queue_harvest(modeladmin, request, queryset, 'normal-stage')


queue_harvest_normal_stage.short_description = 'Queue harvest to CouchDB stage'


def queue_image_harvest(modeladmin, request, queryset, rq_queue):
    success = False
    collections_to_harvest = []
    collections_invalid = []
    for collection in queryset:
        if 'prod' in rq_queue and not collection.ready_for_publication:
            collections_invalid.append(
                (collection,
                 'Not ready for production. Check "ready for publication" '
                 'to harvest to production'))
        else:
            collections_to_harvest.append(collection)
    msg, success = run_script_for_queryset(
            IMAGE_HARVEST_SCRIPT,
            collections_to_harvest,
            rq_queue,
            collection_attr='url_api',
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not harvestable. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join(
                (msg_invalid,
                 '#{} {} - {}; '.format(coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


def queue_image_harvest_normal_stage(modeladmin, request, queryset):
    return queue_image_harvest(modeladmin, request, queryset, 'normal-stage')


queue_image_harvest_normal_stage.short_description = 'Queue image harvest to' \
                                                     ' CouchDB stage'


def queue_sync_couchdb(modeladmin, request, queryset):
    success = False
    rq_queue = 'normal-production'
    collections_to_harvest = []
    collections_invalid = []
    msg = ''
    for collection in queryset:
        if not collection.ready_for_publication:
            collections_invalid.append(
                (collection,
                 'Not ready for production. Check "ready for publication" '
                 'to sync to production'))
        else:
            collections_to_harvest.append(collection)
    msg, success = run_script_for_queryset(
            SYNC_COUCHDB_SCRIPT,
            collections_to_harvest,
            rq_queue,
            collection_attr='url_api',
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not syncable. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid, '#{} {} - {}; '.format(
                coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


queue_sync_couchdb.short_description = ''.join(
        ('Queue sync from CouchDB stage to CouchDB production'))


def set_ready_for_publication(modeladmin, request, queryset):
    '''Set the ready_for_publication to True for the queryset'''
    c_success = []
    for collection in queryset:
        collection.ready_for_publication = True
        collection.save()
        c_success.append(collection)
    msg = 'Set {} collections to "ready for publication"'.format(
        len(c_success))
    modeladmin.message_user(request, msg, level=messages.SUCCESS)


set_ready_for_publication.short_description = "Set ready for publication True"


def queue_sync_to_solr(modeladmin, request, queryset, rq_queue):
    success = False
    collections_to_sync = []
    collections_invalid = []
    for collection in queryset:
        if 'prod' in rq_queue and not collection.ready_for_publication:
            collections_invalid.append((collection,
                                        'Not ready for production. Check '
                                        '"ready for publication" to harvest '
                                        'to production'))
        else:
            collections_to_sync.append(collection)
    msg, success = run_script_for_queryset(
            SYNC_TO_SOLR_SCRIPT,
            collections_to_sync,
            rq_queue,
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not syncable. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid, '#{} {} - {}; '.format(
                coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


def queue_sync_to_solr_normal_stage(modeladmin, request, queryset):
    return queue_sync_to_solr(
            modeladmin,
            request,
            queryset,
            'normal-stage')

queue_sync_to_solr_normal_stage.short_description = 'Queue sync from CouchDB' \
        ' stage to Solr stage'


def queue_sync_to_solr_normal_production(modeladmin, request, queryset):
    return queue_sync_to_solr(
        modeladmin,
        request,
        queryset,
        'normal-production')

queue_sync_to_solr_normal_production.short_description = 'Queue sync from ' \
        'CouchDB production to Solr production'


def queue_delete_from_solr(modeladmin, request, queryset, rq_queue):
    success = False
    collections_to_delete = []
    collections_invalid = []
    for collection in queryset:
        if 'prod' in rq_queue and not collection.ready_for_publication:
            collections_invalid.append((collection,
                                        'Not ready for production. Check '
                                        '"ready for publication" to harvest '
                                        'to production'))
        else:
            collections_to_delete.append(collection)
    msg, success = run_script_for_queryset(
            DELETE_FROM_SOLR_SCRIPT,
            collections_to_delete,
            rq_queue,
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not deletable. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid, '#{} {} - {}; '.format(
                coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


def queue_delete_from_solr_normal_stage(modeladmin, request, queryset):
    return queue_delete_from_solr(
            modeladmin,
            request,
            queryset,
            'normal-stage')

queue_delete_from_solr_normal_stage.short_description = 'Queue deletion ' \
        'of documents from Solr stage'


def queue_delete_from_solr_normal_production(modeladmin, request, queryset):
    return queue_delete_from_solr(
        modeladmin,
        request,
        queryset,
        'normal-production')

queue_delete_from_solr_normal_production.short_description = 'Queue deletion' \
        ' of documents from Solr production'


def queue_deep_harvest(modeladmin, request, queryset, rq_queue):
    success = False
    collections_to_deep_harvest = []
    collections_invalid = []
    for collection in queryset:
        if collection.harvest_type != 'NUX':
            collections_invalid.append((collection,
                                        'Not a Nuxeo collection'))
        else:
            collections_to_deep_harvest.append(collection)
    msg, success = run_script_for_queryset(
            DEEP_HARVEST_SCRIPT,
            collections_to_deep_harvest,
            rq_queue,
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not in Nuxeo. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid, '#{} {} - {}; '.format(
                coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


def queue_deep_harvest_normal_stage(modeladmin, request, queryset):
    return queue_deep_harvest(
            modeladmin,
            request,
            queryset,
            'normal-stage')

queue_deep_harvest_normal_stage.short_description = 'Queue Nuxeo deep ' \
        'harvest (only add new files)'

def queue_deep_harvest_replace(modeladmin, request, queryset, rq_queue):
    success = False
    collections_to_deep_harvest = []
    collections_invalid = []
    for collection in queryset:
        if collection.harvest_type != 'NUX':
            collections_invalid.append((collection,
                                        'Not a Nuxeo collection'))
        else:
            collections_to_deep_harvest.append(collection)
    msg, success = run_script_for_queryset(
            DEEP_HARVEST_SCRIPT_REPLACE,
            collections_to_deep_harvest,
            rq_queue,
            user=request.user)
    if collections_invalid:
        msg_invalid = '{} collections not in Nuxeo. '.format(
            len(collections_invalid))
        for coll, reason in collections_invalid:
            msg_invalid = ''.join((msg_invalid, '#{} {} - {}; '.format(
                coll.id, coll.name, reason)))
        modeladmin.message_user(request, msg_invalid, level=messages.ERROR)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success

def queue_deep_harvest_replace_normal_stage(modeladmin, request, queryset):
    return queue_deep_harvest_replace(
            modeladmin,
            request,
            queryset,
            'normal-stage')

queue_deep_harvest_replace_normal_stage.short_description = 'Queue Nuxeo deep' \
        ' harvest (replace all files)'


def queue_delete_couchdb_collection(modeladmin, request, queryset, rq_queue):
    success = False
    msg, success = run_script_for_queryset(
            DELETE_COUCHDB_SCRIPT,
            queryset,
            rq_queue,
            user=request.user)
    if success:
        modeladmin.message_user(request, msg, level=messages.SUCCESS)
    else:
        modeladmin.message_user(request, msg, level=messages.ERROR)
    return msg, success


def queue_delete_couchdb_collection_stage(modeladmin, request, queryset):
    return queue_delete_couchdb_collection(
            modeladmin,
            request,
            queryset,
            'normal-stage')

queue_delete_couchdb_collection_stage.short_description = 'Queue deletion ' \
        'of documents from CouchDB stage '


def queue_delete_couchdb_collection_production(modeladmin, request, queryset):
    return queue_delete_couchdb_collection(
            modeladmin,
            request,
            queryset,
            'normal-production')

queue_delete_couchdb_collection_production.short_description = 'Queue ' \
        'deletion of documents from CouchDB production'


def retrieve_solr_counts(modeladmin, request, queryset):
    collections_search = SOLR_select(
        facet="true",
        facet_field="collection_url",
        facet_limit=-1,
        rows="0"
    )
    collection_facets = collections_search.facet_counts.get(
        'facet_fields', {}).get('collection_url')
    for collection in queryset:
        solr_count = collection_facets.get(collection.url_api, 0)
        collection.solr_count = solr_count
        collection.solr_last_updated = timezone.now()
        collection.save()
    return None

retrieve_solr_counts.short_description = 'Retrieve Solr counts'

def export_as_csv(modeladmin, request, queryset):
    queryset = queryset.filter(ready_for_publication=True)

    field_names = ['id', 'name', 'url_local', 'url_oac',
                   'description', 'url_harvest']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=collections.csv'
    writer = csv.writer(response)
    writer.writerow(field_names + ['repositories'])

    for obj in queryset:
        row = [getattr(obj, field) for field in field_names]
        repos = ' :: '.join([repo.__str__() for repo in obj.repository.all()])
        row.append(repos)
        writer.writerow(row)

    return response


export_as_csv.short_description = 'Export selected as CSV'

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
