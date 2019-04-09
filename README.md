# Collection Registry

[![Build Status](https://travis-ci.org/ucldc/avram.png?branch=master)](https://travis-ci.org/ucldc/avram)

Playing around with a django app for managing a registry of UC Libraries
Digital Collections.

## notes

```
virtualenv --no-site-packages .
source bin/activate
pip install -r requirements.txt --use-mirrors
```

Using msyql? add:

```
pip install MySQL-python==1.2.4
```

## load

```
python manage.py syncdb
python manage.py migrate
python manage.py loaddata library_collection/fixtures/campus.json
python manage.py loaddata library_collection/fixtures/collection.json
python manage.py collectstatic

```

```
export DJANGO_SETTINGS_MODULE=collection_registry.test_settings
python library_collection/util/sync_oac_repositories.py
```

## Test:
The remoteuser shibboleth login won't work when testing. Use the collection_registry.test_settings module for testing, it adds the typical Django authentication module to the AUTHENTICATION_BACKENDS list.

```
python manage.py test --settings=collection_registry.test_settings  library_collection
```

This also works for local development.

```
python manage.py runserver --settings=collection_registry.test_settings
```
 


License
-------

Copyright © 2014, Regents of the University of California
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, 
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation 
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this 
  software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
