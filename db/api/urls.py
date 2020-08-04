"""SatNOGS DB django rest framework API url routings"""
from django.urls import path
from rest_framework import routers

from db.api import views

ROUTER = routers.DefaultRouter()

ROUTER.register(r'artifacts', views.ArtifactView)
ROUTER.register(r'modes', views.ModeView)
ROUTER.register(r'satellites', views.SatelliteView)
ROUTER.register(r'transmitters', views.TransmitterView)
ROUTER.register(r'telemetry', views.TelemetryView)

API_URLPATTERNS = ROUTER.urls

API_URLPATTERNS += [
    path('recent_decoded_cnt/<int:norad>', views.recent_decoded_cnt, name='recent_decoded_cnt'),
]
