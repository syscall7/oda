from .base import *

DEBUG = False
COMPRESS_ENABLED = True

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     'odapython3',
        'USER':     'postgres',
        'PASSWORD': 'password',
        'HOST':     'db',         # Set to empty string for localhost.
        'PORT':     '',                  # Set to empty string for default.
    }
}

if os.environ.get('ODA_ALLOWED_HOSTS'):
    ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ODA_ALLOWED_HOSTS').split(',')]

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/var/oda'

# File storage settings
# Credentials Must be Stored According to
# https://developers.google.com/identity/protocols/application-default-credentials
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = os.environ.get('ODA_GOOGLE_STORAGE_BUCKET_NAME', 'oda')
