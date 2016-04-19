from django.conf.urls import url
from django.http import HttpResponse

from .. import views

urlpatterns = [
    url(r'^$', lambda _: HttpResponse('Dummy view'), name='dummy-view'),
    url(r'^login/$', views.login, {
        'template_name': 'login.html',
        }, name='login'),
    url(
        r'^logout/$', views.logout, {
            'template_name': 'logout.html',
            'next_page': 'dummy-view',
        }, name='logout'
    ),
    url(
        r'^password_change/$', views.password_change, {
            'template_name': 'login.html',
        }, name='password_change'
    ),
    url(
        r'^password_change_done/$', views.password_change_done, {
            'template_name': 'done.html',
        }, name='password_change_done'
    ),
    url(
        r'^reset-password/$', views.reset_password, {
            'template_name': 'dummy.html',
        }, name='reset_password'
    ),
    url(
        r'^reset-password/$', views.reset_password_done, {
            'template_name': 'dummy.html',
        }, name='reset_password_done'
    ),
]
