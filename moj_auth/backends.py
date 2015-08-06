from . import api_client, get_user_model

class MojBackend(object):

    """
    Django authentication backend which authenticates against the api
    server using oauth2.

    Client Id and Secret can be changed in settings.
    """

    def authenticate(self, username=None, password=None):
        """
        Returns a valid `MojUser` if the authentication is successful
        or None if the credentials were wrong.
        """
        data = api_client.authenticate(username, password)
        if not data:
            return

        UserModel = get_user_model()
        return UserModel(
            data.get('pk'), data.get('token'), data.get('user_data')
        )

    def get_user(self, pk, token, user_data):
        UserModel = get_user_model()
        return UserModel(pk, token, user_data)
