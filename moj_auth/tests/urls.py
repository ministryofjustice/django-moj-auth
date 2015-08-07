from django.conf.urls import url

from .. import views

urlpatterns = [
    url(r'^login/$', views.login, {
        'template_name': 'login.html',
        }, name='login'),
    url(
        r'^logout/$', views.logout, {
            'template_name': 'login.html',
            'next_page': '/login',
        }, name='logout'
    ),
]