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

URL_HARVEST_BASE = 'http://http://dsc.cdlib.org/search?facet=type-tab&style=cui&raw=1&relation='
URL_GITHUB_RAW_BASE = 'https://raw.githubusercontent.com/ucldc/oac_collections/master/az_titles/'
FILE_SUFFIX = '_titles.tsv'
TITLE_PREFIXES = [ alpha for alpha in string.lowercase]
TITLE_PREFIXES.append('0-9')

def parse_ark(url):
    '''parse the ark out & return'''
    return ''.join(('ark:', url.split('ark:')[1].strip()))

def url_harvest(url_findingaid):
    '''Return the xtf search url that gives us our base for OAC harvesting.
    '''
    ark = parse_ark(url_findingaid) 
    return ''.join((URL_HARVEST_BASE, ark))

def main():
    '''Do the syncing, should probably break down for testing....
    '''
    for prefix in TITLE_PREFIXES:
        url_file = ''.join((URL_GITHUB_RAW_BASE, prefix, FILE_SUFFIX))
        print url_file
        # some of the files have blank lines, doesn't work well with csv
        new_input = []
        for l in urllib.urlopen(url_file).readlines():
            if len(l) > 10:
                new_input.append(l)
        print "PROCESSING ", str(len(new_input)), " COLLECTIONS for ", prefix
        #reader = csv.reader(urllib.urlopen(url_file), dialect='excel-tab')
        reader = csv.reader(new_input, dialect='excel-tab')
        #skip first row
        reader.next()
        n = n_new = n_up = 0
        for url_oac, name, ark_repo in reader:
            n += 1
            c = repo = None
            try:
                c = Collection.objects.filter(url_oac=url_oac)
            except Collection.DoesNotExist:
                pass
            if c:
                #update with OAC info
                if len(c) != 1:
                    print "DUPLICATE url_oac:", str([c])
                    next
                c = c[0]
                n_up += 1
                c.name = name
                if not c.url_harvest:
                    c.url_harvest = url_harvest(url_oac)
            else:
                #create new collection
                c = Collection(name=name, url_oac=url_oac, url_harvest=url_harvest(url_oac))
                n_new +=1
            try:
                repo = Repository.objects.get(ark=ark_repo)
                c.repository.add(repo)
            except Repository.DoesNotExist:
                pass
            c.save()
    print "FOR PREFIX ", prefix, " SYNCED ", str(n), " UPDATED:", str(n_up), " ADDED:", str(n_new)

if __name__=='__main__':
    import datetime
    start = datetime.datetime.now()
    print "STARTING AT", start
    main()
    end = datetime.datetime.now()
    print "ENDED AT", end
    print "ELAPSED", end-start
