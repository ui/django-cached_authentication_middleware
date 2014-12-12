# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def auth_preprocessor(user, request):
    user.username = 'test_auth'
    return user
