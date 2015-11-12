from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.request import QueryDict
from django.test import SimpleTestCase
from django.utils.encoding import force_text
import mock
import responses

from moj_auth import SESSION_KEY, BACKEND_SESSION_KEY, \
    AUTH_TOKEN_SESSION_KEY, USER_DATA_SESSION_KEY
from moj_auth import api_client

from .utils import generate_tokens


@mock.patch('moj_auth.backends.api_client')
class LoginViewTestCase(SimpleTestCase):
    """
    Tests that the login flow works as expected.
    """

    def setUp(self):
        self.login_url = reverse('login')

    def test_success(self, mocked_api_client):
        """
        Successful authentication.
        """

        user_pk = 100
        credentials = {
            'username': 'my-username',
            'password': 'my-password'
        }
        token = generate_tokens()
        user_data = {
            'first_name': 'My First Name',
            'last_name': 'My Last Name',
            'username': credentials['username'],
        }
        mocked_api_client.authenticate.return_value = {
            'pk': user_pk,
            'token': token,
            'user_data': user_data
        }

        # login
        response = self.client.post(
            self.login_url, data=credentials
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self.client.session[SESSION_KEY], user_pk
        )
        self.assertEqual(
            self.client.session[BACKEND_SESSION_KEY],
            settings.AUTHENTICATION_BACKENDS[0]
        )
        self.assertDictEqual(
            self.client.session[AUTH_TOKEN_SESSION_KEY], token
        )
        self.assertDictEqual(
            self.client.session[USER_DATA_SESSION_KEY], user_data
        )

    def test_invalid_credentials(self, mocked_api_client):
        """
        The User submits invalid credentials.
        """
        # mock the connection, return invalid credentials
        mocked_api_client.authenticate.return_value = None

        response = self.client.post(
            self.login_url, data={
                'username': 'my-username',
                'password': 'wrong-password'
            }, follow=True
        )

        form = response.context_data['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['__all__'],
            [force_text(form.error_messages['invalid_login'])]
        )
        self.assertEqual(len(self.client.session.items()), 0)  # nothing in the session


class LogoutViewTestCase(SimpleTestCase):
    """
    Tests the logout flow works as expected
    """

    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    @mock.patch('moj_auth.backends.api_client')
    def login(self, mocked_api_client):
        user_pk = 100
        credentials = {
            'username': 'my-username',
            'password': 'my-password',
        }
        token = generate_tokens()
        user_data = {
            'first_name': 'My First Name',
            'last_name': 'My Last Name',
            'username': credentials['username'],
        }
        mocked_api_client.authenticate.return_value = {
            'pk': user_pk,
            'token': token,
            'user_data': user_data,
        }

        # login
        response = self.client.post(self.login_url, data=credentials,
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        return token

    def mock_revocation_response(self):
        responses.add(
            responses.POST,
            api_client.REVOKE_TOKEN_URL,
            status=200,
            content_type='application/json'
        )

    @responses.activate
    def test_logout_clears_session(self):
        self.login()

        self.mock_revocation_response()

        # logout
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)

        # nothing in the session
        self.assertEqual(len(self.client.session.items()), 0)

    @responses.activate
    def test_logout_triggers_token_revocation_request(self):
        token = self.login()

        self.mock_revocation_response()

        # logout
        response = self.client.get(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)

        # token revocation endpoint called with correct details
        self.assertEqual(len(responses.calls), 1)
        revocation_call = responses.calls[0]
        revocation_call_data = QueryDict(revocation_call.request.body)
        revocation_call_data = dict(
            (key, revocation_call_data.get(key, getattr(mock.sentinel, key)))
            for key in ['token', 'client_id', 'client_secret']
        )
        expected_revocation_call_data = {
            'token': token['access_token'],
            'client_id': settings.API_CLIENT_ID,
            'client_secret': settings.API_CLIENT_SECRET,
        }
        self.assertDictEqual(revocation_call_data, expected_revocation_call_data)
