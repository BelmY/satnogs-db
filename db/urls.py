""" Base Django URL mapping for SatNOGS DB"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from allauth import urls as allauth_urls
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from db.api.urls import API_URLPATTERNS
from db.base.urls import BASE_URLPATTERNS

# pylint: disable=C0103
handler404 = 'db.base.views.custom_404'
handler500 = 'db.base.views.custom_500'

urlpatterns = [
    # Base
    url(r'^', include(BASE_URLPATTERNS)),

    # Accounts
    url(r'^accounts/', include(allauth_urls)),

    # API
    url(r'^api/', include(API_URLPATTERNS)),

    # Admin
    url(r'^admin/', admin.site.urls),
]

# Auth0
if settings.AUTH0:
    urlpatterns += [url(r'^', include('auth0login.urls'))]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
