# Collection Registry

[![Build Status](https://travis-ci.org/ucldc/avram.png?branch=master)](https://travis-ci.org/ucldc/avram)

Playing around with a django app for managing a registry of UC Libraries
Digital Collections.

## Installation

### Clone repo:

```sh
cd ~/Projects       # or wherever you like to put source code
git clone git@github.com:ucldc/avram.git
```

### Make sure you're running Python 3.7.16:

Install pyenv https://github.com/pyenv/pyenv, then run 

```sh
cd ~/Projects/avram     # or wherever you cloned this repo
python --version        # should be Python 3.7.16, if not:
pyenv install 3.7.16
pyenv rehash
python --version        # should be Python 3.7.16
pyenv version-origin    # should be avram/.python-version
```

### Create virtual environment and install Avram requirements

```sh
cd ~/Projects/avram
python3 -m venv ~/.envs/registry
source ~/.envs/registry/bin/activate
pip install -r requirements.txt
```

### Install Exhibit Application
The exhibit app code can be placed anywhere, as long as a link is established from `exhibitapp/exhibits/` to `avram/exhibits/`, here I've put the avram and exhibitapp folders next to each other. 

```sh
cd ~/Projects
git clone git@github.com:ucldc/exhibitapp.git
cd exhibitapp
pip install -r requirements.txt
brew install libmagic           # https://pypi.org/project/python-magic/
cd ../avram
ln -s ../exhibitapp/exhibits/
cp env.local.in env.local
```

Modify env.local with solr connection details then:
```sh
source env.local
```

### Install Publishing Projects Application
The publishing projects app code can be placed anywhere, as long as a link is established from `publishing_projects/` to `avram/publishing_projects`, here I've put the avram and publishing_project folders next to each other.

```sh
cd ~Projects
git clone git@github.com:ucldc/publishing_projects.git
cd avram
ln -s ../publishing_projects
```

### Install OAI Application
The OAI app code can be placed anywhere, as long as a link is established from `oaiapp/oai` to `avram/oai`, here I've put the avram and oai folders next to each other.

```sh
cd ~Projects
git clone git@github.com:ucldc/oaiapp.git
cd avram
ln -s ../oaiapp/oai
```

### [Optional] Using msyql? add:

```sh
pip install MySQL-python==1.2.4
```

## Data Setup

### Create the database: 
```sh
python manage.py migrate
```

### Dump data from a production instance:
```sh
python manage.py dumpdata library_collection -a --format=json --indent=2 --natural-foreign --natural-primary -o library_collection.json

python manage.py dumpdata exhibits -a --format=json --indent=2 --natural-foreign --natural-primary -o exhibits.json

python manage.py dumpdata oai -a --format=json --indent=2 --natural-foreign --natural-primary -o oai.json

python manage.py dumpdata publishing_projects -a --format=json --indent=2 --natural-foreign --natural-primary -o publishing_projects.json
```

scp it to your local machine

### Load data
```sh
python manage.py loaddata fixtures/library_collection.json
python manage.py loaddata fixtures/exhibits.json
python manage.py loaddata fixtures/publishing_projects.json
python manage.py loaddata fixtures/oai.json
```

### Load static files
```sh
python manage.py collectstatic
```

### Create super user
```sh
python manage.py createsuperuser --settings=collection_registry.test_settings
```

### Run dev server
```sh
python manage.py runserver --settings=collection_registry.test_settings
```

## Test:
The remoteuser shibboleth login won't work when testing. Use the collection_registry.test_settings module for testing, it adds the typical Django authentication module to the AUTHENTICATION_BACKENDS list.

```
python manage.py test --settings=collection_registry.test_settings  library_collection
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
