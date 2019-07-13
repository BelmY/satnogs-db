"""SatNOGS DB django rest framework API url routings"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from rest_framework import routers

from db.api import views

ROUTER = routers.DefaultRouter()

ROUTER.register(r'modes', views.ModeView)
ROUTER.register(r'satellites', views.SatelliteView)
ROUTER.register(r'transmitters', views.TransmitterView)
ROUTER.register(r'telemetry', views.TelemetryView)

API_URLPATTERNS = ROUTER.urls
