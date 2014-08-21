#! /usr/bin/env python
'''Sync the OAC collections to the collection registry.
We will match on oac_url and update titles.
Create new registry collections if the oac_url is not in the system.
'''
import set_avram_lib_path
import string
import urllib
import csv

from library_collection.models import Collection, Repository

from django.contrib.admin import actions

URL_HARVEST_BASE = 'http://dsc.cdlib.org/search?facet=type-tab&style=cui&raw=1&relation='
URL_GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/ucldc/oac_collections/master/az_titles/'
FILE_SUFFIX = '_titles.tsv'
TITLE_PREFIXES = [ alpha for alpha in string.lowercase]
TITLE_PREFIXES.append('0-9')

DEFAULT_ITEM_ENRICHMENT = '''/select-id,
/oai-to-dpla,
/cleanup_value,
/move_date_values?prop=sourceResource%2Fsubject,
/move_date_values?prop=sourceResource%2Fspatial,
/shred?prop=sourceResource%2Fspatial&delim=--,
/enrich-subject,
/enrich_date,
/enrich-type,
/enrich-format,
/enrich_location,
/scdl_enrich_location,
/geocode,
/scdl_geocode_regions,
/copy_prop?prop=sourceResource%2Fpublisher&to_prop=dataProvider&create=True,
/cleanup_language,
/enrich_language,
/lookup?prop=sourceResource%2Flanguage%2Fname&target=sourceResource%2Flanguage%2Fname&substitution=iso639_3,
/lookup?prop=sourceResource%2Flanguage%2Fname&target=sourceResource%2Flanguage%2Fiso639_3&substitution=iso639_3&inverse=True,
/copy_prop?prop=provider%2Fname&to_prop=dataProvider&create=True&no_overwrite=True,
/lookup?prop=sourceResource%2Fformat&target=sourceResource%2Fformat&substitution=scdl_fix_format,
/set_prop?prop=sourceResource%2FstateLocatedIn&value=California,
/enrich_location?prop=sourceResource%2FstateLocatedIn,
/oac-thumbnail,
/oac-to-sourceResource
'''

def parse_ark(url):
    '''parse the ark out & return'''
    return ''.join(('ark:', url.split('ark:')[1].strip()))

def url_harvest(url_findingaid):
    '''Return the xtf search url that gives us our base for OAC harvesting.
    '''
    ark = parse_ark(url_findingaid) 
    return ''.join((URL_HARVEST_BASE, ark))

def print_progress(c, status):
    try:
        print("{}: {} {}".format(status, c.id, c.name.encode('utf-8')))
    except UnicodeDecodeError, e:
        try:
            print("{}: {} {}".format(status, c.id, c.name.encode('latin-1')))
        except UnicodeDecodeError, e:
            print("{}: {}".format(status, c.id))

def sync_collections_for_url(url_file):
    new_input = []
    for l in urllib.urlopen(url_file).readlines():
        if len(l) > 10: #hokey blank line check, also drops first line
            new_input.append(l)
    #reader = csv.reader(urllib.urlopen(url_file), dialect='excel-tab')
    reader = csv.reader(new_input, dialect='excel-tab')
    #skip first row
    reader.next()
    n = n_new = n_up = 0
    for url_oac, name, ark_repo, online_items in reader:
        online_items = True if online_items == 'true' else False
        n += 1
        c = repo = None
        c = Collection.objects.filter(url_oac=url_oac)
        if not c:
            c = Collection.objects.filter(url_oac=url_oac+'/')
        if c:
            #update with OAC info
            if len(c) != 1:
                print "DUPLICATE url_oac:", str([c])
                next
            c = c[0]
            n_up += 1
            c.name = name
            if online_items:# and not c.url_harvest:
                print_progress(c, "UPDATE")
                c.url_harvest = url_harvest(url_oac)
                c.harvest_type = 'OAC'
                c.enrichments_item = DEFAULT_ITEM_ENRICHMENT
        else:
            #create new collection
            c = Collection(name=name, url_oac=url_oac)
            if online_items:
                print_progress(c, "NEW")
                c.url_harvest = url_harvest(url_oac)
                c.harvest_type = 'OAC'
                c.enrichments_item = DEFAULT_ITEM_ENRICHMENT
            n_new +=1
            c.save() #need to save here to get id for later add of repo
        try:
            repo = Repository.objects.get(ark=ark_repo)
            c.repository.add(repo)
            if repo.campus.count():
                for campus in repo.campus.all():
                    c.campus.add(campus)
        except Repository.DoesNotExist:
            pass
        c.save()
    return n, n_up, n_new

def main(title_prefixes=TITLE_PREFIXES, url_github_raw_base=URL_GITHUB_RAW_BASE):
    '''Do the syncing, should probably break down for testing....
    '''
    n_total = n_updated = n_new = 0
    prefix_totals = []
    for prefix in title_prefixes:
        url_file = ''.join((url_github_raw_base, prefix, FILE_SUFFIX))
        # some of the files have blank lines, doesn't work well with csv
        n, n_up, n_nw = sync_collections_for_url(url_file)
        prefix_totals.append((prefix, n, n_up, n_nw))
        n_total += n
        n_updated += n_up
        n_new += n_nw
        print "PREFIX {0} -> TOTAL OAC:{1} UPDATED:{2} NEW:{3}".format(prefix, n, n_up, n_new)
    return n_total, n_updated, n_new, prefix_totals 

if __name__=='__main__':
    import datetime
    start = datetime.datetime.now()
    print "STARTING AT", start
    n_total, n_updated, n_new, prefix_totals = main()
    end = datetime.datetime.now()
    print "ENDED AT", end
    print "ELAPSED", end-start
    print "OAC COLLECTIONS TOTAL:{0}, UPDATED:{1}, NEW:{2}".format(n_total, n_updated, n_new)
    print "BY PREFIX: [<prefix>, <num OAC>, <num updated>, <num new>]"
    print prefix_totals
