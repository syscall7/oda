import os
from django.core.wsgi import get_wsgi_application

try:
    filename = '/etc/oda/settings.py'
    settings_py = open(filename, 'r').read()
    # print('Read settings.py as: \n' + settings_py)
    exec(compile(settings_py, filename, 'exec'))
except Exception as e:
    print('Missing /etc/oda/settings.py, assuming environment variables are set ...' + str(e))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oda.settings.production")
application = get_wsgi_application()
