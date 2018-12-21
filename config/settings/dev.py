from .common import *
from .secrets import PSQL_PASS

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

INSTALLED_APPS += ['debug_toolbar', ]
INTERNAL_IPS = ['127.0.0.1', '10.49.20.50', '10.49.20.40']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

STATIC_URL = '/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'timeslots',
        'USER': 'timeslots',
        'PASSWORD': PSQL_PASS
    }
}
