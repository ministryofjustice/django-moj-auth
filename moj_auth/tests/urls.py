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
            'template_name': 'login.html',
            'next_page': 'dummy-view',
        }, name='logout'
    ),
]
