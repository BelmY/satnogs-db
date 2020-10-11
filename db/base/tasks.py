"""SatNOGS DB Celery task functions"""
import csv
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
from satellite_tle import fetch_all_tles, fetch_tle_from_celestrak
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from db.base.models import DemodData, ExportedFrameset, Satellite, Tle
from db.base.utils import cache_statistics, decode_data, get_tle_sources, update_latest_tle_sets

LOGGER = logging.getLogger('db')


@shared_task
def check_celery():
    """Dummy celery task to check that everything runs smoothly."""
    LOGGER.info('check_celery has been triggered')


@shared_task
def update_satellite(norad_id, update_name=True):
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

    satellite.save()

    if satellite_created:
        print('Created satellite {}: {}'.format(satellite.norad_cat_id, satellite.name))
    else:
        print('Updated satellite {}: {}'.format(satellite.norad_cat_id, satellite.name))


@shared_task
def update_tle_sets():
    """Task to update all satellite TLEs"""
    satellites = Satellite.objects.exclude(status='re-entered').exclude(status='future')
    catalog_norad_ids = set()
    for satellite in satellites:
        # Check if satellite follows a NORAD ID and it is officially announced
        if satellite.norad_follow_id and satellite.norad_follow_id < 99000:
            catalog_norad_ids.add(satellite.norad_follow_id)
        # Check if satellite has a NORAD ID that is officially announced
        elif satellite.norad_cat_id < 99000:
            catalog_norad_ids.add(satellite.norad_cat_id)

    other_sources = get_tle_sources()

    print("==Fetching TLEs==")
    tles = fetch_all_tles(catalog_norad_ids, **other_sources)

    for satellite in satellites:
        norad_id = satellite.norad_cat_id
        if satellite.norad_follow_id:
            norad_id = satellite.norad_follow_id

        if norad_id in tles.keys():
            for source, tle in tles[norad_id]:
                try:
                    sgp4_tle = twoline2rv(tle[1], tle[2], wgs72)
                except ValueError:
                    print(
                        '[ERROR] {} - {} - {}: TLE malformed'.format(
                            satellite.name, norad_id, source
                        )
                    )
                    continue

                try:
                    last_tle_from_source = Tle.objects.filter(
                        satellite=satellite, tle_source=source
                    ).latest('updated')
                    sgp4_last_tle = twoline2rv(
                        last_tle_from_source.tle1, last_tle_from_source.tle2, wgs72
                    )

                    if (sgp4_tle.epoch == sgp4_last_tle.epoch
                            and last_tle_from_source.tle0 == tle[0]  # noqa: W503
                            and last_tle_from_source.tle1 == tle[1]  # noqa: W503
                            and last_tle_from_source.tle2 == tle[2]):  # noqa: W503
                        print(
                            '[EXISTS] {} - {} - {}: TLE set already exists'.format(
                                satellite.name, norad_id, source
                            )
                        )
                        continue

                except Tle.DoesNotExist:
                    pass

                Tle.objects.create(
                    tle0=tle[0], tle1=tle[1], tle2=tle[2], satellite=satellite, tle_source=source
                )

                print(
                    '[ADDED] {} - {} - {}: TLE set is added'.format(
                        satellite.name, norad_id, source
                    )
                )
        else:
            print('[NOT FOUND] {} - {}: TLE set wasn\'t found'.format(satellite.name, norad_id))
    update_latest_tle_sets()


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

    if period is not None:
        if period == 1:
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
def decode_all_data(norad_id):
    """Task to trigger a full decode of data for a satellite."""
    decode_data(norad_id=norad_id, redecode=True)


@shared_task
def decode_recent_data():
    """Task to trigger a partial/recent decode of data for all satellites."""
    satellites = Satellite.objects.all()

    for obj in satellites:
        try:
            decode_data(norad_id=obj.norad_cat_id)
        except Exception:  # pylint: disable=W0703
            # an object could have failed decoding for a number of reasons,
            # keep going
            continue


@shared_task
def decode_current_frame(norad_id, demoddata_id):
    """Task to trigger a decode of a current frame for a satellite."""
    decode_data(norad_id=norad_id, demoddata_id=demoddata_id)
