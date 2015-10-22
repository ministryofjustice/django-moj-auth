from requests.exceptions import ConnectionError

from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from .exceptions import Unauthorized


class AuthenticationForm(forms.Form):
    """
    Authentication form used for authenticating users during the login process.
    """
    username = forms.CharField(label=_("Username"), max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct username and password. "
                           "Note that both fields may be case-sensitive."),
        'connection_error': _("The API Server seems down, please try again later."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                self.user_cache = authenticate(
                    username=username, password=password
                )
                # if authenticate returns None it means that the
                # credentials were wrong
                if self.user_cache is None:
                    raise Unauthorized
            except ConnectionError:
                # in case of problems connecting to the api server
                raise forms.ValidationError(
                    self.error_messages['connection_error'],
                    code='connection_error',
                )
            except Unauthorized:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
