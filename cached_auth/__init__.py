VERSION = (0, 1, 1)

from django.conf import settings
from django.contrib.auth import get_user, SESSION_KEY
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.functional import SimpleLazyObject

from django.contrib.auth.models import AnonymousUser, User


CACHE_KEY = 'cached_auth_middleware:%s'


try:
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
    profile_model = models.get_model(app_label, model_name)
except (ValueError, AttributeError):
    profile_model = None


def invalidate_cache(sender, instance, **kwargs):
    if isinstance(instance, User):
        key = CACHE_KEY % instance.id
    else:
        key = CACHE_KEY % instance.user_id
    cache.delete(key)


def get_cached_user(request):
    if not hasattr(request, '_cached_user'):
        try:
            key = CACHE_KEY % request.session[SESSION_KEY]
            user = cache.get(key)
        except KeyError:
            user = AnonymousUser()

        if user is None:
            user = get_user(request)

            # Try to populate profile cache if profile is installed
            if profile_model:
                try:
                    user.get_profile()
                # Handle exception for user with no profile and AnonymousUser
                except (profile_model.DoesNotExist, AttributeError):
                    pass
            cache.set(key, user)
        request._cached_user = user
    return request._cached_user


class Middleware(object):

    def __init__(self):
        post_save.connect(invalidate_cache, sender=User)
        post_delete.connect(invalidate_cache, sender=User)
        if profile_model:
            post_save.connect(invalidate_cache, sender=profile_model)
            post_delete.connect(invalidate_cache, sender=profile_model)

    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.user = SimpleLazyObject(lambda: get_cached_user(request))
