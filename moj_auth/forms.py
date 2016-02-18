from django import forms
from django.contrib.auth import authenticate, password_validation
from django.utils.translation import ugettext_lazy as _
from form_error_reporting import GARequestErrorReportingMixin
from requests.exceptions import ConnectionError
from slumber.exceptions import HttpClientError

from .exceptions import Unauthorized
from . import api_client


class AuthenticationForm(GARequestErrorReportingMixin, forms.Form):
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


class PasswordChangeForm(GARequestErrorReportingMixin, forms.Form):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_incorrect': _("Your old password was entered incorrectly. "
                                "Please enter it again."),
    }
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput)
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput,
                                    help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, request=None, user=None, *args, **kwargs):
        self.request = request
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def clean(self):
        if self.is_valid():
            old_password = self.cleaned_data.get('old_password')
            new_password = self.cleaned_data.get('new_password2')
            try:
                api_client.get_connection(self.request).change_password.post(
                    {'old_password': old_password, 'new_password': new_password}
                )
            except HttpClientError:
                raise forms.ValidationError(
                    self.error_messages['password_incorrect'],
                    code='invalid_login'
                )
