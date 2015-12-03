from unittest import mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseForbidden
from django.test import SimpleTestCase, override_settings

middleware = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'moj_auth.csrf.CsrfViewMiddleware',
    'moj_auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
csrf_failure = 'moj_auth.csrf.csrf_failure'
templates = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': False,
    'OPTIONS': {
        'context_processors': ['django.contrib.messages.context_processors.messages'],
        'loaders': ['moj_auth.tests.utils.DummyTemplateLoader']
    },
}]


@override_settings(MIDDLEWARE_CLASSES=middleware,
                   TEMPLATES=templates,
                   CSRF_FAILURE_VIEW=csrf_failure)
class CsrfTestCase(SimpleTestCase):
    def setUp(self):
        self.mocked_api_client = mock.patch('moj_auth.backends.api_client')
        mocked_api_client = self.mocked_api_client.start()
        mocked_api_client.authenticate.return_value = {
            'pk': 1,
            'token': 'abc',
            'user_data': {'first_name': 'First', 'last_name': 'Last',
                          'username': 'test'}
        }

        self.client = self.client_class(enforce_csrf_checks=True)
        self.login_url = reverse('login')

    def tearDown(self):
        self.mocked_api_client.stop()

    def assertInvalidCsrfResponse(self, response):
        self.assertEqual(response.status_code, 403)
        messages = '\n'.join(str(message) for message in response.context['messages'])
        self.assertIn('Please try again', messages)

    def assertValidCsrfResponse(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.has_header('location'))

    def test_missing_csrf_cookie(self):
        response = self.client.post(self.login_url, data={
            'username': 'test',
            'password': '1234',
        })
        self.assertInvalidCsrfResponse(response)

    def test_invalid_csrf_token(self):
        self.client.get(self.login_url)
        response = self.client.post(self.login_url, data={
            'username': 'test',
            'password': '1234',
            'csrfmiddlewaretoken': 'invalid',
        })
        self.assertInvalidCsrfResponse(response)

    def test_successful_csrf_challenge(self):
        self.client.get(self.login_url)
        csrf_token = self.client.cookies[settings.CSRF_COOKIE_NAME]
        response = self.client.post(self.login_url, data={
            'username': 'test',
            'password': '1234',
            'csrfmiddlewaretoken': csrf_token.value,
        })
        self.assertValidCsrfResponse(response)

    @mock.patch('django.views.csrf.csrf_failure')
    def test_turning_off_csrf_failure_override(self, mocked_csrf_failure):
        from moj_auth.csrf import default_csrf_behaviour
        from moj_auth.views import login

        default_csrf_behaviour(login)
        mocked_csrf_failure.return_value = HttpResponseForbidden(b'Django CSRF response')
        response = self.client.post(self.login_url, data={
            'username': 'test',
            'password': '1234',
        })
        self.assertTrue(mocked_csrf_failure.called)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'Django CSRF response')
        login.no_moj_csrf = False
