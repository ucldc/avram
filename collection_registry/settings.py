import os
import sys

def getenv(variable, default):
    ''' getenv wrapper that decodes the same as python 3 in python 2
    '''
    try:  # decode for python2
        return os.getenv(variable, default).decode(sys.getfilesystemencoding())
    except AttributeError:
        return os.getenv(variable, default)


DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

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

DJANGO_CACHE_TIMEOUT = int(getenv('DJANGO_CACHE_TIMEOUT', 60 * 15))  # seconds


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'assets')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'admin_bootstrap/static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&amp;7xo6r-s5w_x6xmm+t8$r-c_-o-=kkc_9z$zgx7hgi%tw995#^'

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'collection_registry.middleware.ThreadLocals',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

AUTHENTICATION_BACKENDS = (
    'collection_registry.backends.RegistryUserBackend',
)

from django.urls import reverse_lazy

#LOGIN_REDIRECT_URL = reverse_lazy('library_collection.views.home')
LOGIN_REDIRECT_URL = "/"

ROOT_URLCONF = 'collection_registry.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'collection_registry.wsgi.application'

APPEND_SLASH = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': (
            os.path.join(SITE_ROOT, '..', 'templates'),
            os.path.join(SITE_ROOT, 'templates'),
            os.path.join(SITE_ROOT, '..', 'library_collection', 'templates'),
            os.path.join(SITE_ROOT, '..', 'oai', 'templates')
        ),
        'OPTIONS': {
            'builtins': ["exhibits.templatetags.exhibit_extras"],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'library_collection.context_processors.active_tab',
                'library_collection.context_processors.google_verification_code',
                'exhibits.context_processors.settings'
            ],
        }
    },
]

# When EXHIBIT_PREVIEW = False, show only exhibits, themes, lesson plans, and essays marked 'published'
# When EXHIBIT_PREVIEW = True, show ALL exhibits, themes, lesson plans, and essays
EXHIBIT_PREVIEW = bool(getenv('UCLDC_EXHIBIT_PREVIEW', False))
THUMBNAIL_URL = getenv('UCLDC_THUMBNAIL_URL',
                          'http://localhost:8888/')  # `python thumbnail.py`
CALISPHERE = False
EXHIBIT_TEMPLATE = 'exhibitBase.html'
SOLR_URL = getenv('UCLDC_SOLR_URL', 'http://localhost:8983/solr')
SOLR_API_KEY = getenv('UCLDC_SOLR_API_KEY', '')

OAI_RESULTS_LIMIT = 100
OAI_RESUMPTION_TOKEN_SALT = getenv('OAI_RESUMPTION_TOKEN_SALT', 'AAaaBBbbCCcc')

INSTALLED_APPS = (
    'exhibits.apps.ExhibitsConfig', 
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'library_collection',
    'publishing_projects',
    'oai',
    # 'rest_framework',
    #'dbdump',
)

ALLOWED_HOSTS = ['dsc-registry2-dev.cdlib.org', 'localhost', '127.0.0.1']

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TASTYPIE_DEFAULT_FORMATS = ['json', 'xml']

try:
    from collection_registry.local_settings import *
except ImportError:
    pass
