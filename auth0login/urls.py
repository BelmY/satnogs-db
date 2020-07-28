"""SatNOGS DB Auth0 login module URL routers"""
from django.conf.urls import include
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('', include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
    path('', include(('social_django.urls', 'social'), namespace='social')),
]
