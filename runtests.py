#!/usr/bin/env python

import os
import sys

from django.conf import settings
import django


DEFAULT_SETTINGS = dict(
    DEBUG=True,
    ROOT_URLCONF='moj_auth.tests.urls',
    AUTHENTICATION_BACKENDS=(
        'moj_auth.backends.MojBackend',
    ),
    SESSION_ENGINE='django.contrib.sessions.backends.signed_cookies',
    MESSAGE_STORAGE='django.contrib.messages.storage.session.SessionStorage',
    OAUTHLIB_INSECURE_TRANSPORT=True,
    API_CLIENT_ID='test-client-id',
    API_CLIENT_SECRET='test-client-secret',
    API_URL='http://test/url',
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'moj_auth.middleware.AuthenticationMiddleware',
    ),
    INSTALLED_APPS=(
        'django.contrib.sessions',
        'moj_auth',
    ),
    TEMPLATE_LOADERS=(
        'moj_auth.tests.utils.DummyTemplateLoader',
    )
)


def runtests():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    # Compatibility with Django 1.7's stricter initialization
    if hasattr(django, 'setup'):
        django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    try:
        from django.test.runner import DiscoverRunner
        runner_class = DiscoverRunner
        test_args = ['moj_auth.tests']
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner
        runner_class = DjangoTestSuiteRunner
        test_args = ['tests']

    failures = runner_class(
        verbosity=1, interactive=True, failfast=False).run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
