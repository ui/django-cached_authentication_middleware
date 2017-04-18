VERSION = (0, 2, 2)

from django.conf import settings
from django.contrib.auth import get_user, SESSION_KEY
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.utils.functional import SimpleLazyObject

from django.contrib.auth.models import AnonymousUser

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

CACHE_KEY = 'cached_auth_middleware:%s'


try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model


try:
    app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
    profile_model = get_model(app_label, model_name)
except (ValueError, AttributeError):
    profile_model = None


def profile_preprocessor(user, request):
    """ Cache user profile """
    if profile_model:
        try:
            user.get_profile()
        # Handle exception for user with no profile and AnonymousUser
        except (profile_model.DoesNotExist, AttributeError):
            pass
    return user


user_preprocessor = None
if hasattr(settings, 'CACHED_AUTH_PREPROCESSOR'):
    tmp = settings.CACHED_AUTH_PREPROCESSOR.split(".")
    module_name, function_name = ".".join(tmp[0:-1]), tmp[-1]
    func = getattr(__import__(module_name, fromlist=['']), function_name)
    if callable(func):
        user_preprocessor = func
    else:
        raise Exception("CACHED_AUTH_PREPROCESSOR must be callable with 2 arguments user and request")
else:
    user_preprocessor = profile_preprocessor


def invalidate_cache(sender, instance, **kwargs):
    if isinstance(instance, get_user_model()):
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
            if user_preprocessor:
                user = user_preprocessor(user, request)
            cache.set(key, user)
        request._cached_user = user
    return request._cached_user


class MiddlewareMixin(object):
    """
    Ported from Django 1.11: django.utils.deprecation.MiddlewareMixin
    """
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class Middleware(MiddlewareMixin):

    def __init__(self, *args, **kwargs):
        super(Middleware, self).__init__(*args, **kwargs)

        post_save.connect(invalidate_cache, sender=get_user_model())
        post_delete.connect(invalidate_cache, sender=get_user_model())
        if profile_model:
            post_save.connect(invalidate_cache, sender=profile_model)
            post_delete.connect(invalidate_cache, sender=profile_model)

    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.user = SimpleLazyObject(lambda: get_cached_user(request))
