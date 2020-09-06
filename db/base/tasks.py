"""SatNOGS DB Celery task functions"""
import csv
import json
import logging
import tempfile
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.mail import send_mail
from django.core.validators import URLValidator
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import make_aware
from satellite_tle import fetch_all_tles, fetch_tle_from_celestrak, fetch_tles
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from db.base.models import DemodData, ExportedFrameset, Satellite, Tle
from db.base.utils import cache_statistics, decode_data

LOGGER = logging.getLogger('db')


@shared_task
def check_celery():
    """Dummy celery task to check that everything runs smoothly."""
    LOGGER.info('check_celery has been triggered')


@shared_task
def update_satellite(norad_id, update_name=True, update_tle=True):
    """Task to update the name and/or the tle of a satellite, or create a
       new satellite in the db if no satellite with given norad_id can be found"""

    tle = fetch_tle_from_celestrak(norad_id)

    satellite_created = False
    try:
        satellite = Satellite.objects.get(norad_cat_id=norad_id)
    except Satellite.DoesNotExist:
        satellite_created = True
        satellite = Satellite(norad_cat_id=norad_id)

    if update_name:
        satellite.name = tle[0]

    if update_tle:
        satellite.tle_source = 'Celestrak (satcat)'
        satellite.tle1 = tle[1]
        satellite.tle2 = tle[2]

    satellite.save()

    if satellite_created:
        print('Created satellite {}: {}'.format(satellite.norad_cat_id, satellite.name))
    else:
        print('Updated satellite {}: {}'.format(satellite.norad_cat_id, satellite.name))


@shared_task
def update_all_tle():
    """Task to update all satellite TLEs"""

    satellites = Satellite.objects.exclude(status__exact='re-entered')
    norad_ids = set(int(sat.norad_cat_id) for sat in satellites)

    # Filter only officially announced NORAD IDs
    temporary_norad_ids = {norad_id for norad_id in norad_ids if norad_id >= 99000}
    public_norad_ids = norad_ids - temporary_norad_ids

    tles = fetch_tles(public_norad_ids)

    missing_norad_ids = []
    for satellite in satellites:
        norad_id = satellite.norad_cat_id

        if norad_id not in list(tles.keys()):
            # No TLE available for this satellite
            missing_norad_ids.append(norad_id)
            continue

        source, tle = tles[norad_id]

        if satellite.tle1 and satellite.tle2:
            try:
                current_sat = twoline2rv(satellite.tle1, satellite.tle2, wgs72)
                new_sat = twoline2rv(tle[1], tle[2], wgs72)
                if new_sat.epoch < current_sat.epoch:
                    # Epoch of new TLE is larger then the TLE already in the db
                    continue
            except ValueError:
                LOGGER.error('ERROR: TLE malformed for %s', norad_id)
                continue

        satellite.tle_source = source
        satellite.tle1 = tle[1]
        satellite.tle2 = tle[2]
        satellite.save()

        print('Updated TLE for {}: {} from {}'.format(norad_id, satellite.name, source))

    for norad_id in sorted(missing_norad_ids):
        satellite = satellites.get(norad_cat_id=norad_id)
        print('NO TLE found for {}: {}'.format(norad_id, satellite.name))

    for norad_id in sorted(temporary_norad_ids):
        satellite = satellites.get(norad_cat_id=norad_id)
        print('Ignored {} with temporary NORAD ID {}'.format(satellite.name, norad_id))


@shared_task
def update_tle_sets():
    """Task to update all satellite TLEs"""
    satellites = Satellite.objects.exclude(status='re-entered')
    norad_ids = set(int(sat.norad_cat_id) for sat in satellites)

    # Filter only officially announced NORAD IDs
    catalog_norad_ids = {norad_id for norad_id in norad_ids if norad_id < 99000}

    # Check for TLE custom sources
    other_sources = {}
    if settings.TLE_SOURCES_JSON:
        try:
            sources_json = json.loads(settings.TLE_SOURCES_JSON)
            other_sources['sources'] = list(sources_json.items())
        except json.JSONDecodeError as error:
            print('TLE Sources JSON ignored as it is invalid: {}'.format(error))
    if settings.SPACE_TRACK_USERNAME and settings.SPACE_TRACK_PASSWORD:
        other_sources['spacetrack_config'] = {
            'identity': settings.SPACE_TRACK_USERNAME,
            'password': settings.SPACE_TRACK_PASSWORD
        }

    print("==Fetching TLEs==")
    tles = fetch_all_tles(catalog_norad_ids, **other_sources)

    for satellite in satellites:
        norad_id = satellite.norad_cat_id
        if norad_id in tles.keys():
            for source, tle in tles[norad_id]:
                (tle, created) = Tle.objects.get_or_create(
                    tle0=tle[0], tle1=tle[1], tle2=tle[2], satellite=satellite, tle_source=source
                )
                if created:
                    print(
                        '{} - {} - {}: [ADDED] TLE set is added'.format(
                            satellite.name, norad_id, source
                        )
                    )
                else:
                    print(
                        '{} - {} - {}: [EXISTS] TLE set already exists'.format(
                            satellite.name, norad_id, source
                        )
                    )
        else:
            print('{} - {}: [NOT FOUND] TLE set wasn\'t found'.format(satellite.name, norad_id))


@shared_task
def remove_old_exported_framesets():
    """Task to export satellite frames in csv."""
    old_datetime = make_aware(
        datetime.utcnow() - timedelta(seconds=settings.EXPORTED_FRAMESET_TIME_TO_LIVE)
    )
    exported_framesets = ExportedFrameset.objects.filter(created__lte=old_datetime
                                                         ).exclude(exported_file='')
    for frameset in exported_framesets:
        frameset.exported_file.delete()


@shared_task
def export_frames(norad, user_id, period=None):
    """Task to export satellite frames in csv."""
    exported_frameset = ExportedFrameset()
    exported_frameset.user = get_user_model().objects.get(pk=user_id)
    exported_frameset.satellite = Satellite.objects.get(norad_cat_id=norad)
    exported_frameset.end = datetime.utcnow()

    if period:
        if period == '1':
            exported_frameset.start = make_aware(exported_frameset.end - timedelta(days=7))
            suffix = 'week'
        else:
            exported_frameset.start = make_aware(exported_frameset.end - timedelta(days=30))
            suffix = 'month'
        frames = DemodData.objects.filter(
            satellite=exported_frameset.satellite,
            timestamp__gte=exported_frameset.start,
            timestamp__lte=exported_frameset.end
        )
    else:
        frames = DemodData.objects.filter(
            satellite=exported_frameset.satellite, timestamp__lte=exported_frameset.end
        )
        suffix = 'all'

    filename = '{0}-{1}-{2}-{3}.csv'.format(
        norad, user_id, exported_frameset.end.strftime('%Y%m%dT%H%M%SZ'), suffix
    )

    with tempfile.SpooledTemporaryFile(max_size=16777216, mode='w+') as csv_file:
        writer = csv.writer(csv_file, delimiter='|')
        for obj in frames:
            frame = obj.display_frame()
            if frame is not None:
                writer.writerow([obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'), frame])
        content_file = File(csv_file)
        exported_frameset.exported_file.save(filename, content_file)

    notify_user_export(exported_frameset.exported_file.url, norad, exported_frameset.user.email)


def notify_user_export(url, norad, email):
    """Helper function to email a user when their export is complete"""
    subject = '[satnogs] Your request for exported frames is ready!'
    template = 'emails/exported_frameset.txt'
    url_validator = URLValidator()
    try:
        url_validator(url)
        data = {'url': url, 'norad': norad}
    except ValidationError:
        site = Site.objects.get_current()
        data = {'url': '{0}{1}'.format(site.domain, url), 'norad': norad}
    message = render_to_string(template, {'data': data})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], False)


@shared_task
def notify_transmitter_suggestion(satellite_id, user_id):
    """Helper function to email admin users when a new transmitter suggestion
    is submitted"""
    satellite = Satellite.objects.get(pk=satellite_id)
    user = get_user_model().objects.get(pk=user_id)

    # Notify admins
    admins = get_user_model().objects.filter(is_superuser=True)
    site = Site.objects.get_current()
    subject = '[{0}] A new suggestion for {1} was submitted'.format(site.name, satellite.name)
    template = 'emails/new_transmitter_suggestion.txt'
    saturl = '{0}{1}'.format(
        site.domain, reverse('satellite', kwargs={'norad': satellite.norad_cat_id})
    )
    data = {
        'satname': satellite.name,
        'saturl': saturl,
        'suggestion_count': satellite.transmitter_suggestion_count,
        'contributor': user
    }
    message = render_to_string(template, {'data': data})
    for user in admins:
        try:
            user.email_user(subject, message, from_email=settings.DEFAULT_FROM_EMAIL)
        except Exception:  # pylint: disable=W0703
            LOGGER.error('Could not send email to user', exc_info=True)


@shared_task
def background_cache_statistics():
    """Task to periodically cache statistics"""
    cache_statistics()


# decode data for a satellite, and a given time frame (if provided). If not
# provided it is expected that we want to try decoding all frames in the db.
@shared_task
def decode_all_data(norad):
    """Task to trigger a full decode of data for a satellite."""
    decode_data(norad)


@shared_task
def decode_recent_data():
    """Task to trigger a partial/recent decode of data for all satellites."""
    satellites = Satellite.objects.all()

    for obj in satellites:
        try:
            decode_data(obj.norad_cat_id, period=1)
        except Exception:  # pylint: disable=W0703
            # an object could have failed decoding for a number of reasons,
            # keep going
            continue
