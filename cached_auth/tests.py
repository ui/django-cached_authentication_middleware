from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from cached_auth import CACHE_KEY

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User


class MiddlewareTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='a')
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        cache.clear()

    def test_anonymous(self):
        # Anonymous user doesn't cause cache to be set
        client = Client()
        key = CACHE_KEY % self.user.id
        response = client.get(reverse('admin:index'))
        self.assertEqual(cache.get(key), None)


    def test_cached_middleware(self):
        client = Client()
        key = CACHE_KEY % self.user.id
        self.assertEqual(cache.get(key), None)

        # Visiting admin causes the cache to be populated
        client.login(username='test', password='a')
        response = client.get(reverse('admin:index'))
        self.assertEqual(cache.get(key), self.user)

        # Changing user model invalidates cache
        self.user.save()
        self.assertEqual(cache.get(key), None)

        # Deleting user invalidates cache
        client.get(reverse('admin:index'))
        self.assertEqual(cache.get(key), self.user)
        self.user.delete()
        self.assertEqual(cache.get(key), None)
