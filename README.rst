django-cached_authentication_middleware is a drop in replacement for
``django.contrib.auth``'s built in ``AuthenticationMiddleware``. It tries to
populate ``request.user`` by fetching user data from cache before falling back
to the database.

Installation
------------

* Install via pypi::

    pip install django-cached_authentication_middleware

* Configure ``CACHES`` in django's ``settings.py``::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': '127.0.0.1:11211',
            'TIMEOUT': 36000,
        }
    }

* Replace ``django.contrib.auth.middleware.AuthenticationMiddleware`` with
  ``cached_auth.Middleware`` in ``settings.py``::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        #'django.contrib.auth.middleware.AuthenticationMiddleware'
        'cached_auth.Middleware',
    )

And you're done!

Running Tests
-------------

To run the test suite::

    python tests/runtests.py

To run the test suite with Django custom user (this will run only on Django 1.5)::

    python tests/runtests_custom_user.py

Changelog
---------

Version 0.1.1
=============

* Fixed an error where middleware tries to call "get_profile" on AnonymousUser

Version 0.1
===========

* Initial release
