import os
import slumber
from requests.exceptions import HTTPError
from functools import partial

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

from django.conf import settings

from . import update_token_in_session
from .exceptions import Unauthorized


# set insecure transport depending on settings val
if settings.OAUTHLIB_INSECURE_TRANSPORT:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


REQUEST_TOKEN_URL = '{base_url}/oauth2/token/'.format(
    base_url=settings.API_URL
)


def response_hook(response, *args, **kwargs):
    if response.status_code == 401:
        raise Unauthorized()
    return response


class MoJOAuth2Session(OAuth2Session):
    def request(self, method, url, data=None, headers=None, **kwargs):
        hooks = kwargs.get('hooks', {})
        if 'response' not in hooks:
            hooks['response'] = response_hook
        kwargs['hooks'] = hooks

        return super(MoJOAuth2Session, self).request(
            method, url, data=data, headers=headers, **kwargs
        )


def authenticate(username, password):
    """
    Returns:
        a dict with:
            pk: the pk of the user
            token: dict containing all the data from the api
                (access_token, refresh_token, expires_at etc.)
            user_data: dict containing user data such as
                first_name, last_name etc.
        if the authentication succeeds
        None if the authentication fails
    """
    session = MoJOAuth2Session(
        client=LegacyApplicationClient(
            client_id=settings.API_CLIENT_ID
        )
    )

    try:
        token = session.fetch_token(
            token_url=REQUEST_TOKEN_URL,
            username=username,
            password=password,
            client_id=settings.API_CLIENT_ID,
            client_secret=settings.API_CLIENT_SECRET
        )

        conn = _get_slumber_connection(session)
        user_data = conn.users(username).get()

        return {
            'pk': user_data.get('pk'),
            'token': token,
            'user_data': user_data
        }
    except HTTPError as e:
        # return None if response.status_code == 401
        #   => invalid credentials
        if hasattr(e, 'response') and e.response.status_code == 401:
            return None
        raise(e)
    return None


def get_connection(request):
    """
    Returns a slumber connection configured using the token of the
    logged-in user.

    It raises `Unauthorized` if the user
    is not authenticated.

        response = get_connection(request).my_endpoint.get()
    """
    user = request.user
    if not user:
        raise Unauthorized(u'no such user')

    def token_saver(token, request, user):
        user.token = token
        update_token_in_session(request, token)

    session = MoJOAuth2Session(
        settings.API_CLIENT_ID,
        token=user.token,
        auto_refresh_url=REQUEST_TOKEN_URL,
        auto_refresh_kwargs={
            'client_id': settings.API_CLIENT_ID,
            'client_secret': settings.API_CLIENT_SECRET
        },
        token_updater=partial(token_saver, request=request, user=user)
    )

    return _get_slumber_connection(session)


def _get_slumber_connection(session):
    return slumber.API(
        base_url=settings.API_URL, session=session
    )
