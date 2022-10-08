"""
Django settings for SkyLibrary project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
import sys
import dj_database_url
from pathlib import Path
from environ import Env

from .services import env_var_not_set_handler, LOGS_FILE_NAME

LOGS_DEBUG_FILE_NAME = 'logs_debug.log'

env = Env()
Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default=None)

if not SECRET_KEY:

    SECRET_KEY = os.urandom(32)

    env_var_not_set_handler('SECRET_KEY', context='used random', error_level='CRITICAL')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=None)

if not DEBUG:

    DEBUG = False

    env_var_not_set_handler('DEBUG', context=f'used {DEBUG}', error_level='WARNING')

else:
    DEBUG = DEBUG.lower() == 'true'


ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='unset').split(', ')

if ALLOWED_HOSTS == ['unset']:

    ALLOWED_HOSTS = []

    env_var_not_set_handler('ALLOWED_HOSTS', context='site is not running', error_level='CRITICAL')

INTERNAL_IPS = env('INTERNAL_IPS', default='unset').split(', ')

if INTERNAL_IPS == ['unset']:

    INTERNAL_IPS = []

    env_var_not_set_handler('INTERNAL_IPS', context='not used', error_level='WARNING')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'bootstrap4',
    'crispy_forms',

    'accounts_app',
    'home_page_app',
    'media_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATE_DIR = BASE_DIR.joinpath('templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DB_URL = env('DB_URL', default=None)

DATABASES = {
    'default': dj_database_url.config(default=DB_URL)
}

if not DB_URL:
    env_var_not_set_handler('DB_URL', context='site is not running', error_level='CRITICAL')


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

STATICFILES_DIRS = [
    BASE_DIR.joinpath('static'),
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # Format such as: ""
            'format': '[{levelname}] [{asctime}] path - "{pathname}" function - "{funcName}" process - "{process:d}" '
                      'thread - "{thread:d}" message - "{message}"',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] - "{message}"',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR.joinpath(LOGS_FILE_NAME),
            'formatter': 'verbose',
        },
        'file_debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': BASE_DIR.joinpath(LOGS_DEBUG_FILE_NAME),
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'mail_admins', 'file_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

USE_CACHE = env('USE_CACHE', default='unset')

if USE_CACHE == 'unset':

    USE_CACHE = True

    env_var_not_set_handler('USE_CACHE', context=f'used {USE_CACHE}', error_level='WARNING')

if USE_CACHE:

    CACHE_LOCAL = env('CACHE_LOCAL', default='unset')

    if CACHE_LOCAL == 'unset':

        CACHE_LOCAL = True

        env_var_not_set_handler('CACHE_LOCAL', context=f'used {CACHE_LOCAL}', error_level='WARNING')

    else:
        # needed because env() return string, any string (exclude empty) in bool is True
        CACHE_LOCAL = CACHE_LOCAL.lower() == 'true'

    if CACHE_LOCAL:

        CACHE_LOCATION_DB_TABLE_NAME = env('CACHE_LOCATION_DB_TABLE_NAME', default='unset')

        if CACHE_LOCATION_DB_TABLE_NAME == 'unset':

            CACHE_LOCATION_DB_TABLE_NAME = 'cache'

            env_var_not_set_handler(
                'CACHE_LOCATION_DB_TABLE_NAME',
                context=f'used "{CACHE_LOCATION_DB_TABLE_NAME}" value',
                error_level='WARNING',
            )

        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                'LOCATION': CACHE_LOCATION_DB_TABLE_NAME,
            }
        }

    else:

        CACHE_REDIS_LOCATIONS = env('CACHE_REDIS_LOCATIONS', default='unset').split(', ')

        if CACHE_REDIS_LOCATIONS == ['unset']:
            """
            CACHE_LOCATIONS unset is critical for the project (because it causes an error when loading the template) -->
            we don't use cache otherwise other parts of the project don't work
            """
            env_var_not_set_handler('CACHE_REDIS_LOCATIONS', context='not used', error_level='ERROR')

        else:
            CACHES = {
                'default': {
                    'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                    'LOCATION': CACHE_REDIS_LOCATIONS,
                }
            }


EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=None)

if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # needed for not error response

    if not EMAIL_HOST_USER:
        env_var_not_set_handler('EMAIL_HOST_USER', context='not used', error_level='ERROR')

    if not EMAIL_HOST_PASSWORD:
        env_var_not_set_handler('EMAIL_HOST_PASSWORD', context='not used', error_level='ERROR')

else:

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.yandex.ru'
    EMAIL_PORT = 465
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False

    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    SERVER_EMAIL = EMAIL_HOST_USER


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGES = (
    ('en-us', 'English (US)'),
    ('ru', 'Russian'),
)

LOCALE_PATHS = (
    BASE_DIR.joinpath('locale'),
)


USE_I18N = True

LANGUAGE_CODE = env('LANGUAGE_CODE', default='unset')

if LANGUAGE_CODE == 'unset':

    LANGUAGE_CODE = 'en-us'

    env_var_not_set_handler('LANGUAGE_CODE', context=f'used {LANGUAGE_CODE}', error_level='WARNING')


USE_TZ = True
TIME_ZONE = 'UTC'
USE_L10N = True


APPS_DIR = str(BASE_DIR.joinpath('apps'))
sys.path.insert(0, APPS_DIR)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.joinpath('media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
WSGI_APPLICATION = 'app_main.wsgi.application'
ROOT_URLCONF = 'app_main.urls'
PROJECT_ROOT = BASE_DIR.joinpath('apps')
AUTH_USER_MODEL = 'accounts_app.User'
LOGOUT_REDIRECT_URL = 'logout_successful'
ACCOUNT_ACTIVATION_DAYS = 10
CRISPY_TEMPLATE_PACK = 'bootstrap4'
