""" Base Django URL mapping for SatNOGS DB"""
from allauth import urls as allauth_urls
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.static import serve

from db.api.urls import API_URLPATTERNS
from db.base.urls import BASE_URLPATTERNS

urlpatterns = [
    # Base
    path('', include(BASE_URLPATTERNS)),

    # Accounts
    path('accounts/', include(allauth_urls)),

    # API
    path('api/', include(API_URLPATTERNS)),

    # Admin
    path('admin/', admin.site.urls),
]

# Auth0
if settings.AUTH0:
    urlpatterns += [path('', include('auth0login.urls'))]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
