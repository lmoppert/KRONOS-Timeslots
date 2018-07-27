from common import *
from secrets import AWS_PSQL_PASS

# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'appdb.cbff4zhuzjet.eu-central-1.rds.amazonaws.com',
        'PORT': '5432',
        'NAME': 'timeslots',
        'USER': 'timeslots',
        'PASSWORD': AWS_PSQL_PASS
    }
}
ALLOWED_HOSTS.append('.kronos-timeslots.de')

# Development configuration
INSTALLED_APPS.append('debug_toolbar')
INTERNAL_IPS = ['62.225.176.130']
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# Host static files with S3
INSTALLED_APPS.append('storages')
AWS_STORAGE_BUCKET_NAME = 'timeslots-staticfiles'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
