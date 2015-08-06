import set_avram_lib_path
import argparse

from library_collection.models import Collection
from django.contrib.admin import actions

colls=Collection.objects.exclude(url_harvest='')
for c in colls:
    new_enrich = c.enrichments_item.replace('required-val','filter_fields?keys=sourceResource,\n/required-val')
    c.enrichments_item = new_enrich
    print "CHANGING: {}".format(c.id)
    c.save()
    break
