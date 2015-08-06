import sys
import os
from django.conf import settings
from django.test.runner import DiscoverRunner
import django

settings.configure(DEBUG=True,
    OAUTHLIB_INSECURE_TRANSPORT=True,
    API_CLIENT_ID = 'cashbook',
    API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET', 'cashbook'),
    API_URL = os.environ.get('API_URL', 'http://localhost:8000'),
    INSTALLED_APPS=('django.contrib.auth',
                    'django.contrib.sessions',
                    'moj_auth',))

sys.path.append('')
django.setup()

test_runner = DiscoverRunner()

failures = test_runner.run_tests(['moj_auth'])
if failures:
    sys.exit(failures)
