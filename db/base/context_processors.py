from __future__ import absolute_import, division, print_function, \
    unicode_literals

from django.conf import settings
from django.template.loader import render_to_string
from satnogsdecoders import __version__ as satnogsdecoders_version

from db import __version__


def analytics(request):
    """Returns analytics code."""
    if settings.ENVIRONMENT == 'production':
        return {'analytics_code': render_to_string('includes/analytics.html')}
    else:
        return {'analytics_code': ''}


def stage_notice(request):
    """Displays stage notice."""
    if settings.ENVIRONMENT == 'stage':
        return {'stage_notice': render_to_string('includes/stage_notice.html')}
    else:
        return {'stage_notice': ''}


def auth_block(request):
    """Displays auth links local vs auth0."""
    if settings.AUTH0:
        return {'auth_block': render_to_string('includes/auth_auth0.html')}
    else:
        return {'auth_block': render_to_string('includes/auth_local.html')}


def logout_block(request):
    """Displays logout links local vs auth0."""
    if settings.AUTH0:
        return {'logout_block': render_to_string('includes/logout_auth0.html')}
    else:
        return {'logout_block': render_to_string('includes/logout_local.html')}


def version(request):
    """Displays the current satnogs-db version."""
    return {'version': 'Version: {}'.format(__version__)}


def decoders_version(request):
    """Displays the satnogsdecoders version."""
    return {'decoders_version': 'Decoders Version: {}'.format(satnogsdecoders_version)}
