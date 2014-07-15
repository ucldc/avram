'''Check collections with url_harvest and type OAC and remove url_harvest for collections
that yield no objects from calisphere?
'''
import set_avram_lib_path
from xml.etree import ElementTree as ET
import urllib

from django.contrib.admin import actions

from library_collection.models import Collection

n = n_changed = 0
for c in Collection.objects.filter(harvest_type='OAC'):
    n += 1
    if 'http://http://' in c.url_harvest:
        c.url_harvest = c.url_harvest[7:]
        c.save()
    resp = urllib.urlopen(c.url_harvest)
    crossQueryResult = ET.fromstring(resp.read())
    if int(crossQueryResult.attrib['totalDocs']) == 0:
        print c.url_harvest
        c.url_harvest = ''
        c.harvest_type = 'X'
        c.harvest_extra_data = ''
        c.save()
        n_changed += 1
print "TOTAL: {0} CHANGED: {1}".format(n, n_changed)
