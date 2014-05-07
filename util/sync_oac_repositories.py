#! /usr/bin/env python
'''Sync the OAC respositories to the collection registry.
We will match on ark. Should we automatically update the names? We will for now.
Create new registry repositories if the ark is not in the system.
'''
import set_avram_lib_path
import urllib
import json

from library_collection.models import Repository, Campus

from django.contrib.admin import actions

URL_OAC_REPO_LIST = 'https://voro.cdlib.org/a/djsite/institution/registry-view/'

def main(url_oac_repo_list=URL_OAC_REPO_LIST ):
    '''Synchronize the OAC institutions and the registry repositories'''
    repo_list = json.loads(urllib.urlopen(url_oac_repo_list).read())
    n = n_up = n_new = 0 
    for name, ark, parent_ark in repo_list:
        n += 1
        try:
            repo = Repository.objects.get(ark=ark)
            # udpate name?, only report update when this is true
            if repo.name != name:
                repo.name = name
                repo.save()
                n_up += 1
        except Repository.DoesNotExist:
            repo = Repository(name=name, ark=ark)
            repo.save()
            n_new += 1
            repo = Repository.objects.get(ark=ark)
        if parent_ark:
            try:
                campus = Campus.objects.get(ark=parent_ark)
                repo.campus.add(campus)
                repo.save()
            except Campus.DoesNotExist:
                pass
    return n, n_up, n_new


if __name__=='__main__':
    import datetime
    start = datetime.datetime.now()
    print "STARTING AT", start
    main()
    end = datetime.datetime.now()
    print "ENDED AT", end
    print "ELAPSED", end-start
