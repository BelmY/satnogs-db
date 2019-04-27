from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve

from allauth import urls as allauth_urls
from db.api.urls import api_urlpatterns
from db.base.urls import base_urlpatterns

handler404 = 'db.base.views.custom_404'
handler500 = 'db.base.views.custom_500'

urlpatterns = [
    # Base
    url(r'^', include(base_urlpatterns)),

    # Accounts
    url(r'^accounts/', include(allauth_urls)),

    # API
    url(r'^api/', include(api_urlpatterns)),

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
