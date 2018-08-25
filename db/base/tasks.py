import csv
from datetime import datetime, timedelta

from orbit import satellite

from django.db.models import Count, Max
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.timezone import make_aware
from influxdb import InfluxDBClient

from db.base.models import Satellite, DemodData
from db.base.utils import calculate_statistics
from db.celery import app
from db.base.utils import decode_data


@app.task(task_ignore_result=False)
def check_celery():
    """Dummy celery task to check that everything runs smoothly."""
    pass


@app.task
def update_all_tle():
    """Task to update all satellite TLEs"""
    satellites = Satellite.objects.all()

    for obj in satellites:
        try:
            sat = satellite(obj.norad_cat_id)
        except Exception:
            continue

        tle = sat.tle()
        obj.tle1 = tle[1]
        obj.tle2 = tle[2]
        obj.save()


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
            writer.writerow([obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                             obj.display_frame()])

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
                                settings.INFLUX_DB)
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
