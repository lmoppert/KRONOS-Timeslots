"""Django settings for project kronos-timeslots.com."""
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from os.pathpath import abspath, dirname, join, normpath, basename
from os import environ
from sys import path
import socket

DIR = abspath(dirname(__file__))
BASE_DIR = dirname(dirname(abspath(__file__)))
SITE_NAME = basename(BASE_DIR)
SITE_ROOT = dirname(BASE_DIR)
path.append(BASE_DIR)

try:
    DJANGO_SERVER = environ['DJANGO_SERVER']
except KeyError:
    DJANGO_SERVER = 'Production'

if DJANGO_SERVER == 'Development':
    DEBUG = True
else:
    DEBUG = False

ADMINS = [
    ('Lutz Moppert', 'lutz.moppert@kronosww.com'),
]
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(SITE_ROOT, 'sqlite3.db'),
    }
}

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('de', _('German')),
]
LOCALE_PATHS = [
    join(SITE_ROOT, 'locale'),
]

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = '/var/www/static/'
STATIC_URL = 'http://' + socket.getfqdn() + '/static/'
STATICFILES_DIRS = [
    join(SITE_ROOT, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q5!b8!u$^n2asxv=co07ru7f=oks9xmpahf)3b7e71sygb09&amp;p'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [ normpath(join(SITE_ROOT, 'templates')) ],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.core.context_processors.static",
            "django.contrib.messages.context_processors.messages",
            "django.core.context_processors.request",
        ],
    },
}, ]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'timeslots',
    'crispy_forms',
    'django_tables2',
]

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

# Login URL
LOGIN_URL = "/timeslots/login"
LOGOUT_URL = "/timeslots/logout"
LOGIN_REDIRECT_URL = "/timeslots/"
AUTH_PROFILE_MODULE = 'timeslots.UserProfile'
SESSION_COOKIE_AGE = 86400

# Optional apps used only for development
if DJANGO_SERVER == 'Development':
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]
    INSTALLED_APPS += ['debug_toolbar',]
    INTERNAL_IPS = ['127.0.0.1', '10.49.20.25', '10.49.20.40']

# Look for a local settings file
try:
        from local_settings import *
except:
        pass
