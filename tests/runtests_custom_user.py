#!/usr/bin/env python
import os
import sys
import django

# Only run this test on django 1.5 and above
if django.VERSION < (1, 5):
    sys.exit()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.conf import settings


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
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


settings.configure(DEBUG=True,
                   DATABASES=DATABASES,
                   INSTALLED_APPS=('django.contrib.auth',
                                   'django.contrib.contenttypes',
                                   'django.contrib.sessions',
                                   'django.contrib.admin',
                                   'custom_user',
                                   'cached_auth',
                                   ),
                   CACHES=CACHES,
                   MIDDLEWARE_CLASSES=MIDDLEWARE_CLASSES,
                   ROOT_URLCONF='urls',
                   AUTH_USER_MODEL = 'custom_user.User')

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['cached_auth', ])
if failures:
    sys.exit(failures)
