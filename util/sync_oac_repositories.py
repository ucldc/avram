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
def main():
    '''Synchronize the OAC institutions and the registry repositories'''
    repo_list = json.loads(urllib.urlopen(URL_OAC_REPO_LIST).read())
    for name, ark, parent_ark in repo_list:
        try:
            repo = Repository.objects.get(ark=ark)
            # udpate name?
            if repo.name != name:
                repo.name = name
                repo.save()
        except Repository.DoesNotExist:
            repo = Repository(name=name, ark=ark)
            repo.save()
            repo = Repository.objects.get(ark=ark)
        if parent_ark:
            try:
                print "parent ark", parent_ark, " repo ", repo.name
                campus = Campus.objects.get(ark=parent_ark)
                print "FOUND CAMPUS", campus, " for repo: ", repo.name
                repo.campus.add(campus)
                repo.save()
            except Campus.DoesNotExist:
                pass


if __name__=='__main__':
    import datetime
    start = datetime.datetime.now()
    print "STARTING AT", start
    main()
    end = datetime.datetime.now()
    print "ENDED AT", end
    print "ELAPSED", end-start
