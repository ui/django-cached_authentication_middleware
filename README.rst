django-cached_authentication_middleware is a drop in replacement for
``django.contrib.auth``'s built in ``AuthenticationMiddleware``. It tries to
populate ``request.user`` by fetching user data from cache before falling back
to the database.

Installation
------------

.. image:: https://travis-ci.org/ui/django-cached_authentication_middleware.png?branch=master


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

Cached Auth Preprocessor
------------------------

Sometimes you want to preprocess to ``User`` instance before storing
it into cache. ``cached_auth`` allows you to define
``settings.CACHED_AUTH_PREPROCESSOR``, a callable that takes two arguments, ``user`` & ``request`` and returns a ``User`` instance.

A classic example of this would be to attach ``Profile`` data
to ``User`` object so calling ``request.user.profile`` does not incur a
database hit. Here's how we can implement it.

.. code-block:: python

    def attach_profile(user, request):
        try:
            user.get_profile()
        # Handle exception for user with no profile and AnonymousUser
        except (Profile.DoesNotExist, AttributeError):
            pass
        return user


    # In settings.py:
    CACHED_AUTH_PREPROCESSOR = 'path.to.module.attach_profile'

Running Tests
-------------

To run the test suite::

    python tests/runtests.py

To run the test suite with Django custom user (this will run only on Django 1.5)::

    python tests/runtests_custom_user.py

Changelog
---------

Version 0.2.0
=============

* Added support for Django 1.5's customer user model
* Added ``CACHED_AUTH_PREPROCESSOR`` setting

Version 0.1.1
=============

* Fixed an error where middleware tries to call "get_profile" on AnonymousUser

Version 0.1
===========

* Initial release
