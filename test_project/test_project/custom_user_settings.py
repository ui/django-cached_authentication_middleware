# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .settings import *


INSTALLED_APPS += (
    'test_app_custom_user',
)

AUTH_USER_MODEL = 'test_app_custom_user.User'
