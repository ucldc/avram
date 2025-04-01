import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DJANGO_DB_NAME'),
        'USER': os.environ.get('DJANGO_DB_USER'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD'),
        'HOST': os.environ.get('DJANGO_DB_HOST'),
        'PORT': '',
    }
}
ALLOWED_HOSTS = ['registry.cdlib.org', 'dsc-registry2-prd.cdlib.org']
DEBUG = False

EXHIBIT_PREVIEW = True
THUMBNAIL_URL = 'https://calisphere.org/'
CALISPHERE = False
EXHIBIT_TEMPLATE = 'exhibitBase.html'
SOLR_URL = os.environ.get('SOLR_STAGE_URL')
SOLR_API_KEY = os.environ.get('SOLR_STAGE_API_KEY')
S3_STASH = os.environ.get('S3_STASH')
S3_ID = os.environ.get('S3_ID')

SOLR_OPTS = [
        {
                'version': 'prod',
                'display_name': 'Candidate Index (Solr Prod)',
                'url': os.environ.get('SOLR_URL'),
                'api_key': os.environ.get('SOLR_API_KEY')
        },
        {
                'version': 'stg',
                'display_name': 'Solr Stage',
                'url': os.environ.get('SOLR_STAGE_URL'),
                'api_key': os.environ.get('SOLR_STAGE_API_KEY')
        }
]

GOOGLE_VERIFICATION_CODE = os.environ.get('GOOGLE_VERIFICATION_CODE')

# For exhibits
EXHIBITS_SOLR_URL = os.environ.get('SOLR_STAGE_URL')
EXHIBITS_SOLR_API_KEY = os.environ.get('SOLR_STAGE_API_KEY')
ES_HOST = os.environ.get('ES_HOST')
ES_USER = os.environ.get('ES_USER')
ES_PASS = os.environ.get('ES_PASS')
ES_ALIAS = "rikolti-stg"

MULTI_INDEX = bool(EXHIBITS_SOLR_URL and ES_HOST)
if MULTI_INDEX:
    DEFAULT_INDEX = "es"
elif EXHIBITS_SOLR_URL:
    DEFAULT_INDEX = "solr"
    THUMBNAIL_URL = SOLR_THUMBNAILS
elif ES_HOST:
    DEFAULT_INDEX = "es"
else:
    raise AttributeError("No index or thumbnail server specified")

MWAA_REGISTRY_ROLE_ARN = os.environ.get('MWAA_REGISTRY_ROLE_ARN')
RIKOLTI_EVENTS_QUEUE_URL = os.environ.get('RIKOLTI_EVENTS_QUEUE_URL')
AWS = {"region_name": "us-west-2"}

OPENSEARCH = {
    'endpoint': os.environ.get('OS_ENDPOINT'),
    'user': os.environ.get('OS_USER'),
    'pass': os.environ.get('OS_PASS'),
    'aws_region': "us-west-2"
}
