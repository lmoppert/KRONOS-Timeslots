# Django settings for project project.
import os
import socket

DIR = os.path.abspath(os.path.dirname(__file__))

try:
    DJANGO_SERVER = os.environ['DJANGO_SERVER']
except KeyError:
    DJANGO_SERVER = 'Production'
if DJANGO_SERVER == 'Development':
    DEBUG = True
else:
    DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Lutz Moppert', 'lutz.moppert@kronosww.com'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DIR, 'sqlite3.db'),
    }
}

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'en'
ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
    ('de', ugettext('German')),
)
LOCALE_PATHS = (
    os.path.join(DIR, '..', 'locale'),
)

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = 'http://' + socket.getfqdn() + '/static/'
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q5!b8!u$^n2asxv=co07ru7f=oks9xmpahf)3b7e71sygb09&amp;p'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(DIR, '..', 'templates')
)

INSTALLED_APPS = (
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
)

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

# Login URL
LOGIN_URL = "/timeslots/login"
LOGOUT_URL = "/timeslots/logout"
LOGIN_REDIRECT_URL = "/timeslots/"
AUTH_PROFILE_MODULE = 'timeslots.UserProfile'
SESSION_COOKIE_AGE = 86400

# Optional apps used only for development
if DJANGO_SERVER == 'Development':
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INSTALLED_APPS += ('debug_toolbar','south')
    INTERNAL_IPS = ['127.0.0.1']
    ALWAYS_SHOW_DEBUG_TOOLBAR = True
    DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

# Look for a local settings file
try:
        from local_settings import *
except:
        pass
