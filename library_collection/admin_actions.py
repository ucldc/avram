# -*- coding: utf-8 -*-
import os
import subprocess
import shlex
import django.contrib.messages as messages

HARVEST_SCRIPT = os.environ.get('HARVEST_SCRIPT', os.environ['HOME'] +
                                '/code/harvester/queue_harvest.bash')
IMAGE_HARVEST_SCRIPT = os.environ.get(
        'IMAGE_HARVEST_SCRIPT',
        os.environ['HOME'] + '/code/harvester/queue_image_harvest.bash')
SYNC_COUCHDB_SCRIPT = os.environ.get(
        'SYNC_COUCHDB_SCRIPT',
        os.environ['HOME'] + '/code/harvester/queue_sync_couchdb.bash')
SYNC_TO_SOLR_SCRIPT = os.environ.get(
        'SYNC_TO_SOLR_SCRIPT',
        os.environ['HOME'] + '/code/harvester/queue_sync_to_solr.bash')


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
                                        'Not ready for production. Check '
                                        '"ready for publication" to harvest '
                                        'to production'))
        else:
            collections_to_harvest.append(collection)
    cmd_line = ' '.join((HARVEST_SCRIPT, user.email, rq_queue))
    arg_coll_uri = ';'.join([c.url_api for c in collections_to_harvest])
    cmd_line = ' '.join((cmd_line, arg_coll_uri))
    try:
        subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        success = True
        msg = 'Queued harvest for {} collections: {} CMD: {}'.format(
            len(collections_to_harvest), '  |  '.join(
                [c.name.encode('utf-8') for c in collections_to_harvest]),
            cmd_line)
    except OSError, e:
        if e.errno == 2:
            msg = 'Cannot find {} for harvesting {} collections {}'.format(
                HARVEST_SCRIPT,
                len(collections_to_harvest), '; '.join(
                    [c.name.encode('utf-8') for c in collections_to_harvest]))
        else:
            msg = 'Error: Trying to run {} error-> {}'.format(cmd_line, str(e))
    return msg, success, collections_invalid, collections_to_harvest


def queue_harvest(modeladmin, request, queryset, rq_queue):
    msg, success, collections_invalid, collections_harvested = \
            queue_harvest_for_queryset(request.user, queryset, rq_queue)
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


def queue_harvest_normal_stage(modeladmin, request, queryset):
    return queue_harvest(modeladmin, request, queryset, 'normal-stage')


queue_harvest_normal_stage.short_description = ''.join(
    ('Queue harvest for ', 'collection(s) on ', 'normal queue'))


def queue_harvest_high_stage(modeladmin, request, queryset):
    return queue_harvest(modeladmin, request, queryset, 'high-stage')


queue_harvest_high_stage.short_description = ''.join(
    ('Queue harvest for ', 'collection(s) on high', ' queue'))


def queue_image_harvest_for_queryset(user, queryset, rq_queue):
    '''Start harvest for valid collections in the queryset'''
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
    cmd_line = ' '.join((IMAGE_HARVEST_SCRIPT, user.email,
                         rq_queue))
    arg_coll_uri = ';'.join([c.url_api for c in collections_to_harvest])
    cmd_line = ' '.join((cmd_line, arg_coll_uri))
    try:
        subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        success = True
        msg = 'Queued image harvest for {} collections: {} CMD: {}'.format(
            len(collections_to_harvest), '  |  '.join(
                [c.name.encode('utf-8') for c in collections_to_harvest]),
            cmd_line)
    except OSError, e:
        if e.errno == 2:
            msg = 'Cannot find {} for image harvesting {} '\
                  'collections {}'.format(
                          IMAGE_HARVEST_SCRIPT,
                          len(collections_to_harvest),
                          '; '.join(
                              [c.name.encode('utf-8') for c in
                                  collections_to_harvest])
                    )
        else:
            msg = 'Error: Trying to run {} error-> {}'.format(cmd_line, str(e))
    return msg, success, collections_invalid, collections_to_harvest


def queue_image_harvest(modeladmin, request, queryset, rq_queue):
    msg, success, collections_invalid, collections_harvested = \
            queue_image_harvest_for_queryset(request.user, queryset, rq_queue)
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


def queue_image_harvest_normal_stage(modeladmin, request, queryset):
    return queue_image_harvest(modeladmin, request, queryset, 'normal-stage')


queue_image_harvest_normal_stage.short_description = ''.join(
    ('Queue image ', 'harvest for collection(s) on normal queue'))


def queue_image_harvest_high_stage(modeladmin, request, queryset):
    return queue_image_harvest(modeladmin, request, queryset, 'high-stage')


queue_image_harvest_high_stage.short_description = ''.join(
    ('Queue image ', 'harvest for collection(s) on high queue'))


def queue_sync_couchdb_for_queryset(user, queryset):
    '''Sync couchdb to production for valid collections in the queryset'''
    success = False
    collections_to_harvest = []
    collections_success = []
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
    for collection in collections_to_harvest:
        cmd_line = SYNC_COUCHDB_SCRIPT
        cmd_line = ' '.join((cmd_line, str(collection.id)))
        try:
            subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
            success = True
            collections_success.append(collection)
        except OSError, e:
            if e.errno == 2:
                msg += 'Cannot find {} for syncing {} collections {}'.format(
                    SYNC_COUCHDB_SCRIPT,
                    len(collections_to_harvest), '; '.join([
                        c.name.encode('utf-8') for c in collections_to_harvest
                    ]))
            else:
                msg += 'Error: Trying to run {} error-> {}'.format(cmd_line,
                                                                   str(e))
    if len(collections_success):
        msg += 'Queued sync couchdb for {} collections: {} '.format(
            len(collections_success), '  |  '.join(
                [c.name.encode('utf-8') for c in collections_success]))
    return msg, success, collections_invalid, collections_success


def queue_sync_couchdb(modeladmin, request, queryset):
    msg, success, collections_invalid, collections_harvested = \
            queue_sync_couchdb_for_queryset(request.user, queryset)
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


queue_sync_couchdb.short_description = ''.join(('Queue sync to production ',
                                                'couchdb for collection(s)'))


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


def queue_sync_to_solr_for_queryset(user, queryset, rq_queue):
    '''Queue a sync to solr job for the collection'''
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
    cmd_line = ' '.join((SYNC_TO_SOLR_SCRIPT, rq_queue))
    arg_coll_uri = ';'.join([c.id for c in collections_to_sync])
    cmd_line = ' '.join((cmd_line, arg_coll_uri))
    try:
        subprocess.Popen(shlex.split(cmd_line.encode('utf-8')))
        success = True
        msg = 'Queued sync to solr for {} collections: {} CMD: {}'.format(
            len(collections_to_sync), '  |  '.join(
                [c.name.encode('utf-8') for c in collections_to_sync]),
            cmd_line)
    except OSError, e:
        if e.errno == 2:
            msg = 'Cannot find {} for syncing solr {} collections {}'.format(
                SYNC_TO_SOLR_SCRIPT,
                len(collections_to_sync), '; '.join(
                    [c.name.encode('utf-8') for c in collections_to_sync]))
        else:
            msg = 'Error: Trying to run {} error-> {}'.format(cmd_line, str(e))
    return msg, success, collections_invalid, collections_to_sync


def queue_sync_to_solr(modeladmin, request, queryset, rq_queue):
    msg, success, collections_invalid, collections_harvested = \
            queue_sync_to_solr_for_queryset(request.user, queryset, rq_queue)
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


def queue_sync_to_solr_normal_stage(modeladmin, request, queryset):
    return queue_sync_to_solr(
            modeladmin,
            request,
            queryset,
            'normal-stage')

queue_sync_to_solr_normal_stage.short_description = ''.join(
    ('Queue sync solr index for ', 'collection(s) on ', 'normal-stage'))


def queue_sync_to_solr_normal_production(modeladmin, request, queryset):
    return queue_sync_to_solr(
        modeladmin,
        request,
        queryset,
        'normal-production')

queue_sync_to_solr_normal_production.short_description = ''.join(
    ('Queue sync solr index for ', 'collection(s) on ', 'normal-production'))


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
