import set_avram_lib_path
import argparse

from library_collection.models import Collection
from django.contrib.admin import actions

colls=Collection.objects.exclude(url_harvest='')
for c in colls:
    new_enrich = c.enrichments_item
    last_enrich = None
    while (last_enrich != new_enrich): 
        last_enrich = new_enrich
    	new_enrich = new_enrich.replace('/filter_fields?keys=sourceResource,\n/filt', '/filt',)
    	new_enrich = new_enrich.replace('/filter_fields?keys=sourceResource,\n/req', '/req',)
    new_enrich = new_enrich.replace('required-val','filter_fields?keys=sourceResource,\n/required-val', 1)
    print "OK? {}".format(new_enrich)
    c.enrichments_item = new_enrich
    print "CHANGING: {}".format(c.id)
    c.save()
