"""SatNOGS DB django rest framework API url routings"""
from rest_framework import routers

from db.api import views

ROUTER = routers.DefaultRouter()

ROUTER.register(r'artifacts', views.ArtifactViewSet)
ROUTER.register(r'modes', views.ModeViewSet)
ROUTER.register(r'satellites', views.SatelliteViewSet)
ROUTER.register(r'transmitters', views.TransmitterViewSet)
ROUTER.register(r'telemetry', views.TelemetryViewSet)
ROUTER.register(r'tle', views.LatestTleSetViewSet)

API_URLPATTERNS = ROUTER.urls
