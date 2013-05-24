import sys,os
import os.path
import csv

# BSD 3-clause license

from human_to_bytes import human2bytes

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))

csv_filepathname = os.path.join(pathname, "refine.tsv")
os.environ['DJANGO_SETTINGS_MODULE'] = 'collection_registry.settings'

from library_collection.models import *

dataReader = csv.reader(open(csv_filepathname), delimiter='\t')

for row in dataReader:
    if row[0] != 'File': # Ignore the header row, import everything else
        collection = ProvenancialCollection()
        if row[0] == 'appendixA.csv':
            collection.appendix = 'A'
        if row[0] == 'appendixB.csv':
            collection.appendix = 'B'
        collection.name = row[2]
        collection.description = row[3]
        collection.url_local = row[6]
        if row[7]:
            collection.extent = int(human2bytes(row[7]))
        collection.hosted = row[8]
        collection.metadata_standard = row[10]
        collection.metadata_level = row[11]
        
        if row[9]:
            collection.need_for_dams = Need.objects.get(name = row[9])
        if row[4]:
            collection.status = Status.objects.get(name = row[4])
        if row[5]:
            collection.access_restrictions = Restriction.objects.get(name = row[5])
        collection.save()

        collection.campus.add(Campus.objects.get(slug = row[1]))
