"""
Django settings for djangoapp project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')c1@3c1+t-bp9#o512nu@87f1vpshn$+_x2wpw#y*%yyar6=4m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'ws4redis',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangoapp.vmtemplates',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'djangoapp.urls'

WSGI_APPLICATION = 'djangoapp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data/db/database.sqlite'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

WEBSOCKET_URL = '/ws/'
WS4REDIS_PREFIX = 'ws'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static/').replace('\\','/')
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
	os.path.join(BASE_DIR, 'templates').replace('\\','/'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/').replace('\\','/')

MEDIA_URL = '/media/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'ws4redis.context_processors.default',
)

WSGI_APPLICATION = 'ws4redis.django_runserver.application'

WS4REDIS_EXPIRE = 3600

WS4REDIS_HEARTBEAT = '--heartbeat--'

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_PREFIX = 'session'
# Queue Configuration
QUEUE_PORT = '6000'
AUTHKEY = 'listener'

# Proxy Configuration
# TODO:Improve here to get more machines involved as proxy
PROXY_APP = '/home/tong/noVNC/utils/launch.sh'
PROXY = '192.168.1.231'


# iVIC configuration
IVIC_PORTAL_URL = 'http://192.168.1.160'
IVIC_PORTAL_USER = 'edx-ivic@act.buaa.edu.cn'
IVIC_PORTAL_PASSWD = 'edx-ivic'
IVIC_DB_HOST = '192.168.1.160'
IVIC_DB_USER = 'root'
IVIC_DB_PASSWD = ''
IVIC_DB_PORT = 3306

METHODS = (
    'nfsmount',
)
VSTORES = (
    '192.168.1.160',
)
LOCAL_XML_DIR = os.path.join(BASE_DIR, 'data/xml')
IMG_STORE = '192.168.1.160'
IMG_DIR = '/var/lib/ivic/imgs'
IMG_USERNAME = 'root'
IMG_PASSWD = 'tong'
VSTORE_USERNAME = 'root'
VSTORE_PASSWD = 'tong'
OS_TYPES = (
    'linux',
    'windows',
)
DISTRIBUTIONS = (
    'debain',
    'windows-xp',
    'redhat',
    'windows2000',
    'windows2003',
    'windows2008',
    'windows7',
    'squeeze',
    'centos',
    'fedora',
    'ubuntu',
)
