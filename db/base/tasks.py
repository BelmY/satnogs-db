import csv
import logging
from datetime import datetime, timedelta

from django.db.models import Count, Max
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.timezone import make_aware
from influxdb import InfluxDBClient

from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from satellite_tle import fetch_tle_from_celestrak, fetch_tles

from db.base.models import Satellite, DemodData
from db.base.utils import calculate_statistics
from db.celery import app
from db.base.utils import decode_data

logger = logging.getLogger('db')


@app.task(task_ignore_result=False)
def check_celery():
    """Dummy celery task to check that everything runs smoothly."""
    pass


@app.task
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


@app.task
def update_all_tle():
    """Task to update all satellite TLEs"""

    satellites = Satellite.objects.exclude(status__exact='re-entered')
    norad_ids = set(int(sat.norad_cat_id) for sat in satellites)

    # Filter only officially announced NORAD IDs
    temporary_norad_ids = set(filter(lambda norad_id: norad_id >= 99900, norad_ids))
    public_norad_ids = norad_ids - temporary_norad_ids

    tles = fetch_tles(public_norad_ids)

    missing_norad_ids = []
    for satellite in satellites:
        norad_id = satellite.norad_cat_id

        if norad_id not in tles.keys():
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
                logger.error('ERROR: TLE malformed for ' + norad_id)
                continue

        satellite.tle_source = source
        satellite.tle1 = tle[1]
        satellite.tle2 = tle[2]
        satellite.save()

        print('Updated TLE for {}: {} from {}'.format(norad_id,
                                                      satellite.name,
                                                      source))

    for norad_id in sorted(missing_norad_ids):
        satellite = satellites.get(norad_cat_id=norad_id)
        print('NO TLE found for {}: {}'.format(norad_id, satellite.name))

    for norad_id in sorted(temporary_norad_ids):
        satellite = satellites.get(norad_cat_id=norad_id)
        print('Ignored {} with temporary NORAD ID {}'.format(satellite.name, norad_id))


@app.task
def export_frames(norad, email, uid, period=None):
    """Task to export satellite frames in csv."""
    now = datetime.utcnow()
    if period:
        if period == '1':
            q = now - timedelta(days=7)
            suffix = 'week'
        else:
            q = now - timedelta(days=30)
            suffix = 'month'
        q = make_aware(q)
        frames = DemodData.objects.filter(satellite__norad_cat_id=norad,
                                          timestamp__gte=q)
    else:
        frames = DemodData.objects.filter(satellite__norad_cat_id=norad)
        suffix = 'all'
    filename = '{0}-{1}-{2}-{3}.csv'.format(norad, uid, now.strftime('%Y%m%dT%H%M%SZ'), suffix)
    filepath = '{0}/download/{1}'.format(settings.MEDIA_ROOT, filename)
    with open(filepath, 'w') as f:
        writer = csv.writer(f, delimiter='|')
        for obj in frames:
            frame = obj.display_frame()
            if frame is not None:
                writer.writerow([obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'), frame])

    # Notify user
    site = Site.objects.get_current()
    subject = '[satnogs] Your request for exported frames is ready!'
    template = 'emails/exported_frames.txt'
    data = {
        'url': '{0}{1}download/{2}'.format(site.domain,
                                           settings.MEDIA_URL, filename),
        'norad': norad
    }
    message = render_to_string(template, {'data': data})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], False)


@app.task
def cache_statistics():
    statistics = calculate_statistics()
    cache.set('stats_transmitters', statistics, 60 * 60 * 2)

    satellites = Satellite.objects \
                          .values('name', 'norad_cat_id') \
                          .annotate(count=Count('telemetry_data'),
                                    latest_payload=Max('telemetry_data__timestamp')) \
                          .order_by('-count')
    cache.set('stats_satellites', satellites, 60 * 60 * 2)

    observers = DemodData.objects \
                         .values('observer') \
                         .annotate(count=Count('observer'),
                                   latest_payload=Max('timestamp')) \
                         .order_by('-count')
    cache.set('stats_observers', observers, 60 * 60 * 2)


# resets all decoded data and changes the is_decoded flag back to False
# THIS IS VERY DISTRUCTIVE, but the expectation is that a decode_all_data would
# follow.
@app.task
def reset_decoded_data(norad):
    """DESTRUCTIVE: deletes decoded data from db and/or influxdb"""
    frames = DemodData.objects.filter(satellite__norad_cat_id=norad) \
                              .filter(is_decoded=True)
    for frame in frames:
        frame.payload_decoded = ''
        frame.is_decoded = False
        frame.save()
    if settings.USE_INFLUX:
        client = InfluxDBClient(settings.INFLUX_HOST, settings.INFLUX_PORT,
                                settings.INFLUX_USER, settings.INFLUX_PASS,
                                settings.INFLUX_DB, ssl=settings.INFLUX_SSL)
        client.query('DROP SERIES FROM /.*/ WHERE \"norad\" = \'{0}\''
                     .format(norad))


# decode data for a satellite, and a given time frame (if provided). If not
# provided it is expected that we want to try decoding all frames in the db.
@app.task
def decode_all_data(norad):
    """Task to trigger a full decode of data for a satellite."""
    decode_data(norad)


@app.task
def decode_recent_data():
    """Task to trigger a partial/recent decode of data for all satellites."""
    satellites = Satellite.objects.all()

    for obj in satellites:
        try:
            decode_data(obj.norad_cat_id, period=1)
        except Exception:
            continue
