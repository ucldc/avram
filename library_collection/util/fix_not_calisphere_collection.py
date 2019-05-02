#! /usr/bin/env python
'''
some non calisphere collections are in the database as OAC XML harvest.
set these to have a 'X' None setting for harvest type
results are filtered from the rq failed queue and put in csv
with URL_to_api, URL_for_xtf_search.
'''

#strip the id from api URL and update
from . import set_avram_lib_path
import string
import urllib.request, urllib.parse, urllib.error
import csv

from library_collection.models import Collection
from django.contrib.admin import actions

cids = []
for row in csv.reader(open('xtf-no-results.csv')):
        cid = row[0].strip('/').rsplit('/', 1)[1]
        print('URL: {}  ID: {}'.format(row[0], cid))
        c = Collection.objects.get(id=cid)
        print('C: {}'.format(c))
        c.harvest_type = 'X'
        cids.append(cid)
        c.save()

print(cids)
