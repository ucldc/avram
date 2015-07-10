'''For a harvest_type subset of collections, set the enrichments_item.

Need to make a generic one with pre, post fixes to items for particular
collections

filter on harvest_type which is passed in.

point to a text file that has enrichment string in it.

'''
import set_avram_lib_path
import argparse

from library_collection.models import Collection
from django.contrib.admin import actions

HARVEST_TYPES = []
for t in Collection.HARVEST_TYPE_CHOICES:
    HARVEST_TYPES.append(t[0])

def overwrite_enrichments_for_collection(collection, enrichment):
    collection.enrichments_item = enrichment
    collection.save()

def overwrite_enrichments_for_queryset(qs, enrichment):
    '''Overwrite the enrichments for a queryset
    '''
    for collection in qs:
        overwrite_enrichments_for_collection(collection, enrichment)

def overwrite_enrichments_for_collection_id(cid, enrichment):
    qs = Collection.objects.filter(pk=cid)
    print "RUNNING ON {}".format(qs)
    overwrite_enrichments_for_queryset(qs, enrichment)

def overwrite_enrichments_for_harvest_type(harvest_type, enrichment,
        campus_id=None):
    '''Overwrite the enrichmets_item field for the collections with a 
    given harvest_type
    
    >>> overwrite_enrichments_for_harvest_type('BOGUS', 'BOGUS')
    Traceback (most recent call last):
        ...
    ValueError: BOGUS is not a valid harvest type
    >>> overwrite_enrichments_for_harvest_type('OAC', 'BOGUS')
    Traceback (most recent call last):
        ...
    IOError: [Errno 2] No such file or directory: 'BOGUS'
    >>> import set_avram_lib_path
    >>> import os
    >>> enrich_file = os.path.join(set_avram_lib_path.FILE_DIR, 'enrichments_item_oac.txt')
    >>> overwrite_enrichments_for_harvest_type('OAC', enrich_file)
    '''
    if harvest_type not in HARVEST_TYPES:
        raise ValueError('{} is not a valid harvest type'.format(harvest_type))
    if campus_id:
        qs = Collection.objects.filter(
                harvest_type=harvest_type).filter(campus__id=campus_id)
    else:
        qs = Collection.objects.filter(harvest_type=harvest_type)
    print "RUNNING ON {}".format(qs)
    overwrite_enrichments_for_queryset(qs, enrichment)

if __name__=='__main__':
    parser = argparse.ArgumentParser(
            description='Change the enrichments_item for a harvest type')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--harvest_type',  type=str,
            choices=HARVEST_TYPES,
            help='harvest type code - {}'.format(HARVEST_TYPES)
            )
    group.add_argument('--collection_id', type=int,
            help='collection id to run the enrichment on'
            )
    parser.add_argument('--campus_id', type=int,
            help='Limit to the particualr campus')
    parser.add_argument('enrichment_file',
            help='Text file of comma-separated enrichements list')
                  
    args = parser.parse_args()
    with open(args.enrichment_file) as infoo:
        enrichments_string = infoo.read().strip()
    
    if args.harvest_type:
        overwrite_enrichments_for_harvest_type(args.harvest_type,
                enrichments_string, campus_id=args.campus_id)
    elif args.collection_id:
        overwrite_enrichments_for_collection_id(args.collection_id,
                enrichments_string)
    else:
        print ' '.join(("No collection criteria specified.",
                       "Please specify --harvest_type or",
                       "--collection_id."))
