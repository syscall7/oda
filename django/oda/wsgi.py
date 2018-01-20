import os
from django.core.wsgi import get_wsgi_application

try:
    filename = '/etc/oda/settings.py'
    exec(compile(open(filename, 'rb').read(), filename, 'exec'))
except Exception as e:
    print('Missing /etc/oda/settings.py, assuming environment variables are set ...' + str(e))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oda.settings.production")
application = get_wsgi_application()
