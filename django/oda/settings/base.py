# Django settings for oda_python project.

import os.path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADMINS = (
    ('Anthony', 'anthony@onlinedisassembler.com'),
    ('Davis', 'davis@onlinedisassembler.com'),
    ('Tom', 'tom@onlinedisassembler.com'),
    ('Aaron', 'aaron@onlinedisassembler.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

INTERNAL_IPS = ('127.0.0.1',)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.environ.get('ODA_MEDIA_ROOT', '/var/oda')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

PROJECT_DIR = os.path.dirname(__file__)  # this is not Django setting.

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '..','..','web', 'dist', 'static')
    # os.path.join(PROJECT_DIR, "../odaweb/static")
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    'compressor.finders.CompressorFinder'
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('ODA_SECRET_KEY')

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
# )

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'lazysignup.backends.LazySignupBackend',
)

# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.core.context_processors.debug',
#     'django.core.context_processors.i18n',
#     'django.core.context_processors.media',
#     'django.core.context_processors.static',
#     'django.core.context_processors.request',
#     'django.contrib.auth.context_processors.auth',
#     'django.contrib.messages.context_processors.messages',
#
#     "allauth.account.context_processors.account",
#     "allauth.socialaccount.context_processors.socialaccount",
# )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oda.apps.odaweb.middleware.ThreadLocalMiddleware',
    'oda.apps.odaweb.middleware.LoggingMiddleware',
)

ROOT_URLCONF = 'oda.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'oda.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, "../apps/odaweb/templates/"),
            os.path.join(PROJECT_DIR, "../apps/users/templates/"),
            os.path.join(PROJECT_DIR, "../apps/users/templates/allauth/")
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_USER_MODEL = 'odaweb.OdaUser'

#ALLAUTH Settings
ACCOUNT_ADAPTER = 'oda.apps.users.allauth.AccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'oda.apps.users.allauth.SignupForm'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = '/odaweb/'

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('ODA_EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_PORT = os.environ.get('ODA_EMAIL_PORT', 2525)
EMAIL_HOST_USER = os.environ.get('ODA_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('ODA_EMAIL_HOST_PASSWORD')

INSTALLED_APPS = (
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    # django-storages
    'storages',

    # django_compressor
    'compressor',

    # django-rest-framework
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',

    # https://github.com/kmike/django-widget-tweaks
    'widget_tweaks',

    'lazysignup',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',

    'oda.apps.odaweb'
)

# The code below is from: http://www.tiwoc.de/blog/2013/03/django-prevent-email-notification-on-suspiciousoperation/
# Purpose is to block the annoying emails we get when someone is scanning our site
from django.core.exceptions import SuspiciousOperation


def skip_suspicious_operations(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
    elif record.name == 'django.security.DisallowedHost':
        return False
    return True


# Purpose is to block the annoying emails we get when someone aborts a post by closing the browser, etc.
from django.http import UnreadablePostError


def skip_unreadable_post_errors(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, UnreadablePostError):
            return False
    return True


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': 'oda|%(asctime)s|%(process)5d %(requestNum)s|%(levelname)s|%(remoteAddr)s|(%(module)14s@%(lineno)3d) %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        # Define filter
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        },
        'skip_unreadable_post_errors': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_unreadable_post_errors,
        },
        'request_context': {
            '()': 'oda.apps.odaweb.utils.RequestUserFilter'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations', 'skip_unreadable_post_errors'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['request_context']
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': os.path.join(BASE_DIR, 'logs', 'oda.log'),
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
            'filters': ['request_context']
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        },
        # uncomment this if the database queries are too verbose
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }

    }
}
