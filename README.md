Relevant Imports
================

    moj_auth.forms.AuthenticationForm
    moj_auth.login(request, user)
    moj_auth.logout(request)


Django Settings
===============

    MIDDLEWARE_CLASSES = (
        ...
        'moj_auth.middleware.AuthenticationMiddleware',
        ...
    )

    AUTHENTICATION_BACKENDS = (
        'moj_auth.backends.MojBackend',
    )

If you wish for additional interface methods, you can extend 
moj_auth.models.MojUser, and specify your subclass as MOJ_USER_MODEL.
An example would be adding a property to access a key in the 
user_data dict.

    AUTH_USER_MODEL = 'myapp.MyCustomUser'
    MOJ_USER_MODEL = 'myapp.models.MyCustomUser'

Specify the parameters of the API authentication. API_CLIENT_ID and 
API_CLIENT_SECRET should be unique to your application.

    API_CLIENT_ID = 'xxx'
    API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET', 'xxx')
    API_URL = os.environ.get('API_URL', 'http://localhost:8000')

    OAUTHLIB_INSECURE_TRANSPORT = True