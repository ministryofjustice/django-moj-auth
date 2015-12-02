Usage
=====

.. code-block:: python

    from django.conf.urls import url

    from moj_auth import views

    urlpatterns = [
        url(r'^login/$', views.login, {
            'template_name': 'login.html',
            }, name='login'),
        url(
            r'^logout/$', views.logout, {
                'template_name': 'login.html',
                'next_page': reverse_lazy('login'),
            }, name='logout'
        ),
    ]


Django Settings
===============

.. code-block:: python

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

.. code-block:: python

    MOJ_USER_MODEL = 'myapp.models.MyCustomUser'

Specify the parameters of the API authentication. API_CLIENT_ID and
API_CLIENT_SECRET should be unique to your application.

.. code-block:: python

    API_CLIENT_ID = 'xxx'
    API_CLIENT_SECRET = os.environ.get('API_CLIENT_SECRET', 'xxx')
    API_URL = os.environ.get('API_URL', 'http://localhost:8000')

    OAUTHLIB_INSECURE_TRANSPORT = True
