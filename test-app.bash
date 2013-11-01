#!/usr/bin/env bash

# Just a little reminder to use the collection_registyr.test_settings.py file

python manage.py test --settings=collection_registry.test_settings $1
