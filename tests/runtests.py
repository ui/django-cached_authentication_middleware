#!/usr/bin/env python
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.conf import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

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

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'cached_auth'
)


settings.configure(
    DEBUG=True,
    DATABASES=DATABASES,
    INSTALLED_APPS=INSTALLED_APPS,
    CACHES=CACHES,
    MIDDLEWARE_CLASSES=MIDDLEWARE_CLASSES,
    ROOT_URLCONF='urls'
)


from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['cached_auth', ])

if failures:
    sys.exit(failures)
