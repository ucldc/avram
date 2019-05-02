#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''Sync the OAC respositories to the collection registry.
We will match on ark. Should we automatically update the names? We will for now.
Create new registry repositories if the ark is not in the system.
'''
from . import set_avram_lib_path
import urllib.request, urllib.parse, urllib.error
import json

import django
django.setup()

from library_collection.models import Repository, Campus

from django.contrib.admin import actions

URL_OAC_REPO_LIST = 'https://voro.cdlib.org/a/djsite/institution/registry-view/'

def main(url_oac_repo_list=URL_OAC_REPO_LIST ):
    '''Synchronize the OAC institutions and the registry repositories'''
    n = n_up = n_new = 0 

    # read the JSON from an API URL
    repo_list = json.loads(urllib.request.urlopen(url_oac_repo_list).read())

    for name, ark, parent_ark, parent_name in repo_list:

        # try/except idomatic python; but maybe refactor to use .exists()
        non_uc = not(Campus.objects.filter(ark=parent_ark).exists())

        if non_uc and parent_name:
            full_name = ', '.join([parent_name, name])
        else:
            full_name = name

        # see if repo exists, if not create it
        try:
            repo = Repository.objects.get(ark=ark)
            # udpate name?, only report update when this is true
            if repo.name != full_name:
                repo.name = full_name
                repo.save()
                n_up += 1
        except Repository.DoesNotExist:
            repo = Repository(name=full_name, ark=ark)
            repo.save()
            n_new += 1
            repo = Repository.objects.get(ark=ark)

        # add campus link (UC's)
        if parent_ark:
            try:
                campus = Campus.objects.get(ark=parent_ark)
                repo.campus.add(campus)
                repo.save()
            except Campus.DoesNotExist:
                pass

        n += 1
    # return for unit tests
    return n, n_up, n_new


if __name__=='__main__':
    import datetime
    start = datetime.datetime.now()
    print("STARTING AT", start)
    main()
    end = datetime.datetime.now()
    print("ENDED AT", end)
    print("ELAPSED", end-start)
