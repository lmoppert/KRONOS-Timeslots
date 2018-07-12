from common import *
from secrets import PSQL_PASS

# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'timeslots',
        'USER': 'timeslots',
        'PASSWORD': PSQL_PASS
    }
}
