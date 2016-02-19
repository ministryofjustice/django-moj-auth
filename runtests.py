#!/usr/bin/env python
import argparse
import os
import sys

import django
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.test.runner import DiscoverRunner

DEFAULT_SETTINGS = dict(
    DEBUG=True,
    SECRET_KEY='a' * 24,
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
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'moj_auth',
    ),
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [],
            'loaders': ['moj_auth.tests.utils.DummyTemplateLoader']
        },
    }],
    LOGIN_URL=reverse_lazy('login'),
    LOGOUT_URL=reverse_lazy('logout'),
    LOGIN_REDIRECT_URL=reverse_lazy('dummy-view'),
)


def runtests():
    if 'setup.py' in sys.argv:
        # allows `python setup.py test` as well as `./runtests.py`
        sys.argv = ['runtests.py']

    parser = argparse.ArgumentParser()
    parser.add_argument('test_labels', nargs='*', default=['moj_auth.tests'])
    parser.add_argument('--verbosity', type=int, choices=list(range(4)), default=1)
    parser.add_argument('--noinput', dest='interactive',
                        action='store_false', default=True)
    args = parser.parse_args()
    test_labels = args.test_labels

    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    django.setup()

    failures = DiscoverRunner(verbosity=args.verbosity, interactive=args.interactive,
                              failfast=False).run_tests(test_labels)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
