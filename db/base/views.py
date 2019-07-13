"""Base django views for SatNOGS DB"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.db import OperationalError
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from db.base.forms import TransmitterEntryForm
from db.base.helpers import get_apikey
from db.base.models import SERVICE_TYPE, TRANSMITTER_STATUS, \
    TRANSMITTER_TYPE, DemodData, Mode, Satellite, Transmitter, \
    TransmitterSuggestion
from db.base.tasks import export_frames
from db.base.utils import cache_statistics

LOGGER = logging.getLogger('db')


def home(request):
    """View to render home page.

    :returns: base/home.html
    """
    satellites = Satellite.objects.all()
    transmitter_suggestions = TransmitterSuggestion.objects.count()
    contributors = User.objects.filter(is_active=1).count()
    cached_stats = cache.get('stats_transmitters')
    if not cached_stats:
        try:
            cache_statistics()
            cached_stats = cache.get('stats_transmitters')
        except OperationalError:
            pass
    return render(
        request, 'base/home.html', {
            'satellites': satellites,
            'statistics': cached_stats,
            'contributors': contributors,
            'transmitter_suggestions': transmitter_suggestions
        }
    )


def custom_404(request):
    """Custom 404 error handler.

    :returns: 404.html
    """
    return HttpResponseNotFound(render(request, '404.html'))


def custom_500(request):
    """Custom 500 error handler.

    :returns: 500.html
    """
    return HttpResponseServerError(render(request, '500.html'))


def robots(request):
    """robots.txt handler

    :returns: robots.txt
    """
    data = render(request, 'robots.txt', {'environment': settings.ENVIRONMENT})
    response = HttpResponse(data, content_type='text/plain; charset=utf-8')
    return response


def satellite(request, norad):
    """View to render satellite page.

    :returns: base/satellite.html
    """
    satellite_obj = get_object_or_404(Satellite.objects, norad_cat_id=norad)
    transmitter_suggestions = TransmitterSuggestion.objects.filter(satellite=satellite_obj)
    for suggestion in transmitter_suggestions:
        try:
            original_transmitter = satellite_obj.transmitters.get(uuid=suggestion.uuid)
            suggestion.transmitter = original_transmitter
        except Transmitter.DoesNotExist:
            suggestion.transmitter = None
    modes = Mode.objects.all()
    types = TRANSMITTER_TYPE
    services = SERVICE_TYPE
    statuses = TRANSMITTER_STATUS
    # TODO: this is a horrible hack, as we have to pass the entire cache to the
    # template to iterate on, just for one satellite. See #237
    sats_cache = cache.get('stats_satellites')
    if not sats_cache:
        sats_cache = []

    try:
        latest_frame = DemodData.objects.filter(satellite=satellite_obj).order_by('-id')[0]
    except Exception:
        latest_frame = ''

    return render(
        request, 'base/satellite.html', {
            'satellite': satellite_obj,
            'transmitter_suggestions': transmitter_suggestions,
            'modes': modes,
            'types': types,
            'services': services,
            'statuses': statuses,
            'latest_frame': latest_frame,
            'sats_cache': sats_cache,
            'mapbox_token': settings.MAPBOX_TOKEN
        }
    )


@login_required
def request_export(request, norad, period=None):
    """View to request frames export download.

    This triggers a request to collect and zip up the requested data for
    download, which the user is notified of via email when the celery task is
    completed.
    :returns: the originating satellite page
    """
    export_frames.delay(norad, request.user.email, request.user.pk, period)
    messages.success(
        request, ('Your download request was received. '
                  'You will get an email when it\'s ready')
    )
    return redirect(reverse('satellite', kwargs={'norad': norad}))


@login_required
@require_POST
def transmitter_suggestion(request):
    """View to process transmitter suggestion form

    :returns: the originating satellite page unless an error occurs
    """
    transmitter_form = TransmitterEntryForm(request.POST)
    if transmitter_form.is_valid():
        transmitter = transmitter_form.save(commit=False)
        transmitter.user = request.user
        transmitter.reviewed = False
        transmitter.approved = False
        uuid = transmitter_form.cleaned_data['uuid']
        if uuid:
            transmitter.uuid = uuid
        transmitter.save()

        # Notify admins
        admins = User.objects.filter(is_superuser=True)
        site = get_current_site(request)
        subject = '[{0}] A new suggestion for {1} was submitted'.format(
            site.name, transmitter.satellite.name
        )
        template = 'emails/new_transmitter_suggestion.txt'
        saturl = '{0}{1}'.format(
            site.domain,
            reverse('satellite', kwargs={'norad': transmitter.satellite.norad_cat_id})
        )
        data = {
            'satname': transmitter.satellite.name,
            'saturl': saturl,
            'sitedomain': site.domain,
            'contributor': transmitter.user
        }
        message = render_to_string(template, {'data': data})
        for user in admins:
            try:
                user.email_user(subject, message, from_email=settings.DEFAULT_FROM_EMAIL)
            except Exception:
                LOGGER.error('Could not send email to user', exc_info=True)

        messages.success(
            request,
            ('Your transmitter suggestion was stored successfully. '
             'Thanks for contibuting!')
        )
        return redirect(reverse('satellite', kwargs={'norad': transmitter.satellite.norad_cat_id}))
    else:
        LOGGER.error(
            'Suggestion form was not valid {0}'.format(transmitter_form.errors),
            exc_info=True,
            extra={
                'form': transmitter_form.errors,
            }
        )
        messages.error(request, 'We are sorry, but some error occured :(')
        return redirect(reverse('home'))


def about(request):
    """View to render about page.

    :returns: base/about.html
    """
    return render(request, 'base/about.html')


# TODO: replace this with a link to docs in the wiki which won't require code
# updates to maintain
def faq(request):
    """View to render faq page.

    :returns: base/faq.html
    """
    return render(request, 'base/faq.html')


def stats(request):
    """View to render stats page.

    :returns: base/stats.html
    """
    satellites = cache.get('stats_satellites')
    observers = cache.get('stats_observers')
    # TODO this will never succeed, cache_statistics() runs too long to be live
    if not satellites or not observers:
        try:
            cache_statistics()
        except OperationalError:
            pass
    return render(request, 'base/stats.html', {'satellites': satellites, 'observers': observers})


def statistics(request):
    """Triggers a refresh of cached statistics if the cache does not exist

    :returns: JsonResponse of statistics
    """
    cached_stats = cache.get('stats_transmitters')
    if not cached_stats:
        cache_statistics()
        cached_stats = []
    return JsonResponse(cached_stats, safe=False)


# TODO: this is confusing as we call it "edit" but it is the users "settings"
@login_required
def users_edit(request):
    """View to render user settings page.

    :returns: base/users_edit.html
    """
    token = get_apikey(request.user)
    return render(request, 'base/users_edit.html', {'token': token})
