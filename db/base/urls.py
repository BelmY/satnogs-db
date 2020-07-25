"""Django base URL routings for SatNOGS DB"""
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from django.urls import path

from db.base import views

BASE_URLPATTERNS = (
    [
        url(r'^$', views.home, name='home'),
        url(r'^about/$', views.about, name='about'),
        url(r'^faq/$', views.faq, name='faq'),
        url(r'^satellites/$', views.satellites, name='satellites'),
        url(r'^satellite/(?P<norad>[0-9]+)/$', views.satellite, name='satellite'),
        url(r'^frames/(?P<norad>[0-9]+)/$', views.request_export, name='request_export_all'),
        url(
            r'^frames/(?P<norad>[0-9]+)/(?P<period>[0-9]+)/$',
            views.request_export,
            name='request_export'
        ),
        url(r'^help/$', views.satnogs_help, name='help'),
        url(
            r'^transmitter_suggestion_handler/$',
            views.transmitter_suggestion_handler,
            name='transmitter_suggestion_handler'
        ),
        url(r'^transmitters/$', views.transmitters_list, name='transmitters_list'),
        url(r'^statistics/$', views.statistics, name='statistics'),
        url(r'^stats/$', views.stats, name='stats'),
        url(r'^users/edit/$', views.users_edit, name='users_edit'),
        url(r'^robots\.txt$', views.robots, name='robots'),
        url(r'^search/$', views.search, name='search_results'),
        url(
            r'^update_satellite/(?P<pk>[0-9]+)/$',
            permission_required('base.change_satellite')(views.SatelliteUpdateView.as_view()),
            name='update_satellite'
        ),
        path(
            'create_transmitter/<int:satellite_pk>',
            views.TransmitterCreateView.as_view(),
            name='create_transmitter'
        ),
        path(
            'update_transmitter/<int:pk>',
            views.TransmitterUpdateView.as_view(),
            name='update_transmitter'
        ),
    ]
)
