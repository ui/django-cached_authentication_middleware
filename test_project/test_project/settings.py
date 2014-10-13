# -*- coding: utf-8 -*-
from __future__ import unicode_literals


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'cached_auth',
    'test_app',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 36000,
    }
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'cached_auth.Middleware',
)

ROOT_URLCONF = 'test_project.urls'

SECRET_KEY = 'django-cached-authentication-middleware'
