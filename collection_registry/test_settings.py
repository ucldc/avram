import os
from .settings import *

MIDDLEWARE = [
        #'collection_registry.middleware.RemoteUserMockMiddleware',
        'collection_registry.middleware.BasicAuthMockMiddleware',
] + MIDDLEWARE


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test-db',    # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

MWAA_REGISTRY_ROLE_ARN = os.environ.get('MWAA_REGISTRY_ROLE_ARN', '')
RIKOLTI_EVENTS_QUEUE_URL = os.environ.get('RIKOLTI_EVENTS_QUEUE_URL', '')
AWS = {
    "aws_access_key_id": os.environ.get('AWS_ACCESS_KEY_ID', ''),
    "aws_secret_access_key": os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
    "aws_session_token": os.environ.get('AWS_SESSION_TOKEN', ''),
    "region_name": "us-west-2"
}
