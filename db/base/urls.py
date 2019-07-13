"""Django base URL routings for SatNOGS DB"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from django.conf.urls import url

from db.base import views

BASE_URLPATTERNS = (
    [
        url(r'^$', views.home, name='home'),
        url(r'^about/$', views.about, name='about'),
        url(r'^faq/$', views.faq, name='faq'),
        url(r'^satellite/(?P<norad>[0-9]+)/$', views.satellite, name='satellite'),
        url(r'^frames/(?P<norad>[0-9]+)/$', views.request_export, name='request_export_all'),
        url(
            r'^frames/(?P<norad>[0-9]+)/(?P<period>[0-9]+)/$',
            views.request_export,
            name='request_export'
        ),
        url(
            r'^transmitter_suggestion/$',
            views.transmitter_suggestion,
            name='transmitter_suggestion'
        ),
        url(r'^statistics/$', views.statistics, name='statistics'),
        url(r'^stats/$', views.stats, name='stats'),
        url(r'^users/edit/$', views.users_edit, name='users_edit'),
        url(r'^robots\.txt$', views.robots, name='robots'),
    ]
)
