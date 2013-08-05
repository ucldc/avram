import os, sys
from pprint import pprint as pp

# https://github.com/GoodCloud/django-longer-username/issues/15

pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'collection_registry.settings'

from library_collection.models import *
# http://oac.cdlib.org/institutions/?limit=online
uc_repo_data = [
  ('UCB', [
    'Bancroft Library', 
    'Berkeley Art Museum/Pacific Film Archive', 
    'Environmental Design Archives', 
    'Ethnic Studies Library', 
    'Hearst (Phoebe A.) Museum of Anthropology', 
    'Institute for Research on Labor and Employment Library', 
    'Museum of Vertebrate Zoology', 
    'University Archives', 
  ],),
  ('UCD', [
    'Special Collections', 
    'University Archives', 
  ],),
  ( 'UCI', [
    'Critical Theory Archive', 
    'Southeast Asian Archive', 
    'Special Collections', 
    'University Archives', 
  ],),
  ( 'UCM', [
    'Library and Special Collections', 
  ],),
  ( 'UCR', [
    'California Museum of Photography', 
    'Special Collections and Archives', 
    'Water Resources Collections and Archives', 
  ],),
  ( 'UCSD', [
    'Mandeville Special Collections Library', 
    'Research Data Curation Program', 
    'University Archives', 
  ],),
  ( 'UCSF', [
    'Special Collections', 
    'Tobacco Control Archives', 
  ],),
  ( 'UCSB', [
    'Architecture and Design Collection, Art, Design and Architecture Museum', 
    'Cheadle Center for Biodiversity and Ecological Restoration', 
    'Special Collections', 
  ],),
  ( 'UCSC', [
    'Special Collections and Archives', 
  ],),
  ('UCLA', [
    'Fowler Museum of Cultural History', 
    'Grunwald Center for the Graphic Arts', 
    'Library Special Collections, Center for Oral History Research', 
    'Library Special Collections, Charles E. Young Research Library', 
    'Library Special Collections, Performing Arts', 
  ],),
]

for (campus, repos) in uc_repo_data:
    pp(campus)
    for repo in repos:
        repository = Repository()
        repository.name = repo
        repository.save()
        repository.campus.add(Campus.objects.get(slug=campus))
