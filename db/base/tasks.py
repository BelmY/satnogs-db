"""SatNOGS DB Celery task functions"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import csv
import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import make_aware
from satellite_tle import fetch_tle_from_celestrak, fetch_tles
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from db.base.models import DemodData, Satellite
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
def export_frames(norad, email, uid, period=None):
    """Task to export satellite frames in csv."""
    now = datetime.utcnow()
    if period:
        if period == '1':
            time_period = now - timedelta(days=7)
            suffix = 'week'
        else:
            time_period = now - timedelta(days=30)
            suffix = 'month'
        time_period = make_aware(time_period)
        frames = DemodData.objects.filter(
            satellite__norad_cat_id=norad, timestamp__gte=time_period
        )
    else:
        frames = DemodData.objects.filter(satellite__norad_cat_id=norad)
        suffix = 'all'
    filename = '{0}-{1}-{2}-{3}.csv'.format(norad, uid, now.strftime('%Y%m%dT%H%M%SZ'), suffix)
    filepath = '{0}/download/{1}'.format(settings.MEDIA_ROOT, filename)
    write_export_frames(filepath, frames)
    notify_user_export(filename, norad, email)


def write_export_frames(filepath, frames):
    """Helper function to write exported frames to a specified file"""
    with open(filepath, 'w') as output_file:
        writer = csv.writer(output_file, delimiter='|')
        for obj in frames:
            frame = obj.display_frame()
            if frame is not None:
                writer.writerow([obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'), frame])


def notify_user_export(filename, norad, email):
    """Helper function to email a user when their export is complete"""
    site = Site.objects.get_current()
    subject = '[satnogs] Your request for exported frames is ready!'
    template = 'emails/exported_frames.txt'
    data = {
        'url': '{0}{1}download/{2}'.format(site.domain, settings.MEDIA_URL, filename),
        'norad': norad
    }
    message = render_to_string(template, {'data': data})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], False)


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
