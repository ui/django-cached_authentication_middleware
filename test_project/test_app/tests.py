# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

import cached_auth

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

try:
    # Python 3.4+ includes reload in importlib
    from importlib import reload
except ImportError:
    try:
        # Python 3.3 includes reload in imp
        from imp import reload
    except ImportError:
        # Python 2 includes reload as a builtin
        pass


class MiddlewareTest(TestCase):

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='test', password='a')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        cache.clear()

    def test_anonymous(self):
        # Anonymous user doesn't cause cache to be set
        client = Client()
        key = cached_auth.CACHE_KEY % self.user.id
        client.get(reverse('admin:index'))
        self.assertEqual(cache.get(key), None)

    def test_cached_middleware(self):
        client = Client()
        key = cached_auth.CACHE_KEY % self.user.id
        self.assertEqual(cache.get(key), None)

        # Visiting admin causes the cache to be populated
        client.login(username='test', password='a')
        client.get(reverse('admin:index'))
        self.assertEqual(cache.get(key), self.user)

        # Changing user model invalidates cache
        self.user.save()
        self.assertEqual(cache.get(key), None)

        # Deleting user invalidates cache
        client.get(reverse('admin:index'))
        self.assertEqual(cache.get(key), self.user)
        self.user.delete()
        self.assertEqual(cache.get(key), None)

    @override_settings(CACHED_AUTH_PREPROCESSOR='test_project.utils.auth_preprocessor')
    def test_cached_auth_preprocessor_function(self):
        reload(cached_auth)
        client = Client()
        key = cached_auth.CACHE_KEY % self.user.id
        self.assertEqual(cache.get(key), None)

        client.login(username='test', password='a')
        client.get(reverse('admin:index'))
        user = cache.get(key)
        self.assertEqual(user.username, 'test_auth')
