'''Set up the pythonpath with the necessary libraries to run avram
Add any extra pythonpaths you need in here.
Assumes that this file lives in avram/util directory (one level down from
manage.py
'''
import sys
import os
from os.path import join, abspath, split
import shutil

FILE_DIR = abspath(split(__file__)[0])
AVRAM_DIR = abspath(join(FILE_DIR, '..'))

sys.path.append(FILE_DIR)
sys.path.insert(0, AVRAM_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get('DJANGO_SETTINGS_MODULE', 'collection_registry.settings')
