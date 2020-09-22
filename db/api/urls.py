"""SatNOGS DB django rest framework API url routings"""
from rest_framework import routers

from db.api import views

ROUTER = routers.DefaultRouter()

ROUTER.register(r'artifacts', views.ArtifactView)
ROUTER.register(r'modes', views.ModeView)
ROUTER.register(r'satellites', views.SatelliteView)
ROUTER.register(r'transmitters', views.TransmitterView)
ROUTER.register(r'telemetry', views.TelemetryView)
ROUTER.register(r'tle', views.LatestTleSetView)

API_URLPATTERNS = ROUTER.urls
