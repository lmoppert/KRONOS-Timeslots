"""Django settings for project kronos-timeslots.com."""
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from os.path import abspath, dirname, join, normpath, basename
from sys import path
from .secrets import SECRET_KEY
import socket

DIR = abspath(dirname(__file__))
BASE_DIR = dirname(dirname(abspath(__file__)))
SITE_NAME = basename(BASE_DIR)
SITE_ROOT = dirname(BASE_DIR)
path.append(BASE_DIR)

SECRET_KEY = SECRET_KEY
DEBUG = False
ALLOWED_HOSTS = [
    'kronos-timeslots.com',
    'timeslots.kronosww.com',
    'localhost',
    '127.0.0.1',
]

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

MEDIA_ROOT = '/var/www/static/media/'
MEDIA_URL = 'http://' + socket.getfqdn() + '/static/media/'
STATIC_ROOT = '/var/www/static/'
STATIC_URL = 'http://' + socket.getfqdn() + '/static/'
STATICFILES_DIRS = [
    join(SITE_ROOT, 'static'),
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [normpath(join(SITE_ROOT, 'templates'))],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
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

ROOT_URLCONF = '{}.urls'.format(SITE_NAME)
WSGI_APPLICATION = '{}.wsgi.dev.application'.format(SITE_NAME)

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
    'django_extensions',
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
LOGIN_URL = "/app/login"
LOGOUT_URL = "/app/logout"
LOGIN_REDIRECT_URL = "/app/"
AUTH_PROFILE_MODULE = 'timeslots.UserProfile'
SESSION_COOKIE_AGE = 86400
