import sys
import os
from django.conf import settings
from django.test.runner import DiscoverRunner
import django

settings.configure(DEBUG=True,
    ROOT_URLCONF='moj_auth.tests.urls',
    AUTHENTICATION_BACKENDS = (
        'moj_auth.backends.MojBackend',
    ),
    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies',
    MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage',
    OAUTHLIB_INSECURE_TRANSPORT=True,
    API_CLIENT_ID = 'cashbook',
    API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET', 'cashbook'),
    API_URL = os.environ.get('API_URL', 'http://localhost:8000'),
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'moj_auth.middleware.AuthenticationMiddleware',
    ),
    INSTALLED_APPS=('django.contrib.sessions',
                    'moj_auth',),
    TEMPLATE_LOADERS=('moj_auth.tests.utils.DummyTemplateLoader',)
    )

sys.path.append('')
django.setup()

test_runner = DiscoverRunner()

failures = test_runner.run_tests(['moj_auth'])
if failures:
    sys.exit(failures)
