import logging

from django.db.models import Count, Max
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from db.base.models import Mode, Transmitter, Satellite, Suggestion, DemodData, TRANSMITTER_TYPE
from db.base.forms import SuggestionForm
from db.base.helpers import get_apikey
from db.base.tasks import export_frames, cache_statistics
from _mysql_exceptions import OperationalError


logger = logging.getLogger('db')


def home(request):
    """View to render home page."""
    satellites = Satellite.objects.all()
    transmitters = Transmitter.objects.all().count()
    suggestions = Suggestion.objects.all().count()
    contributors = User.objects.filter(is_active=1).count()
    payloads = DemodData.objects.all().count()
    return render(request, 'base/home.html', {'satellites': satellites,
                                              'transmitters': transmitters,
                                              'contributors': contributors,
                                              'payloads': payloads,
                                              'suggestions': suggestions})


def custom_404(request):
    """Custom 404 error handler."""
    return HttpResponseNotFound(render(request, '404.html'))


def custom_500(request):
    """Custom 500 error handler."""
    return HttpResponseServerError(render(request, '500.html'))


def robots(request):
    data = render(request, 'robots.txt', {'environment': settings.ENVIRONMENT})
    response = HttpResponse(data,
                            content_type='text/plain; charset=utf-8')
    return response


def satellite(request, norad):
    """View to render satellite page."""
    satellite_query = Satellite.objects \
                               .annotate(latest_payload_time=Max('telemetry_data__timestamp'),
                                         payload_frames_count=Count('telemetry_data'))
    satellite = get_object_or_404(satellite_query, norad_cat_id=norad)
    suggestions = Suggestion.objects.filter(satellite=satellite)
    modes = Mode.objects.all()
    types = TRANSMITTER_TYPE
    telemetry_data_count = DemodData.objects.filter(satellite__norad_cat_id=norad,
                                                    is_decoded=True).count()

    try:
        latest_frame = DemodData.objects.get(satellite=satellite,
                                             timestamp=satellite.latest_payload_time)
    except Exception:
        latest_frame = ''

    return render(request, 'base/satellite.html', {'satellite': satellite,
                                                   'suggestions': suggestions,
                                                   'modes': modes,
                                                   'types': types,
                                                   'latest_frame': latest_frame,
                                                   'telemetry_data_count': telemetry_data_count,
                                                   'mapbox_token': settings.MAPBOX_TOKEN})


@login_required
def request_export(request, norad, period=None):
    """View to request frames export download."""
    export_frames.delay(norad, request.user.email, request.user.pk, period)
    messages.success(request, ('Your download request was received. '
                               'You will get an email when it\'s ready'))
    return redirect(reverse('satellite', kwargs={'norad': norad}))


@login_required
@require_POST
def suggestion(request):
    """View to process suggestion form"""
    suggestion_form = SuggestionForm(request.POST)
    if suggestion_form.is_valid():
        suggestion = suggestion_form.save(commit=False)
        suggestion.user = request.user
        suggestion.save()

        # Notify admins
        admins = User.objects.filter(is_superuser=True)
        site = get_current_site(request)
        subject = '[{0}] A new suggestion for {1} was submitted'.format(site.name,
                                                                        suggestion.satellite.name)
        template = 'emails/new_suggestion.txt'
        saturl = '{0}{1}'.format(
            site.domain,
            reverse('satellite', kwargs={'norad': suggestion.satellite.norad_cat_id})
        )
        data = {
            'satname': suggestion.satellite.name,
            'saturl': saturl,
            'sitedomain': site.domain,
            'contributor': suggestion.user
        }
        message = render_to_string(template, {'data': data})
        for user in admins:
            try:
                user.email_user(subject, message, from_email=settings.DEFAULT_FROM_EMAIL)
            except Exception:
                logger.error(
                    'Could not send email to user',
                    exc_info=True
                )

        messages.success(request, ('Your suggestion was stored successfully. '
                                   'Thanks for contibuting!'))
        return redirect(reverse('satellite', kwargs={'norad': suggestion.satellite.norad_cat_id}))
    else:
        logger.error(
            'Suggestion form was not valid {0}'.format(suggestion_form.errors),
            exc_info=True,
            extra={
                'form': suggestion_form.errors,
            }
        )
        messages.error(request, 'We are sorry, but some error occured :(')
        return redirect(reverse('home'))


def about(request):
    """View to render about page."""
    return render(request, 'base/about.html')


def faq(request):
    """View to render faq page."""
    return render(request, 'base/faq.html')


def stats(request):
    """View to render stats page."""
    satellites = cache.get('stats_satellites')
    observers = cache.get('stats_observers')
    if not satellites or not observers:
        try:
            cache_statistics.delay()
        except OperationalError:
            pass
    return render(request, 'base/stats.html', {'satellites': satellites,
                                               'observers': observers})


def statistics(request):
    statistics = cache.get('stats_transmitters')
    if not statistics:
        cache_statistics.delay()
        statistics = []
    return JsonResponse(statistics, safe=False)


@login_required
def users_edit(request):
    """View to render user settings page."""
    token = get_apikey(request.user)
    return render(request, 'base/users_edit.html', {'token': token})
