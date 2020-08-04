"""Miscellaneous functions for SatNOGS DB"""
import binascii
import logging
import math
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Max
from django.utils.timezone import make_aware
from influxdb import InfluxDBClient
from satnogsdecoders import __version__ as decoders_version
from satnogsdecoders import decoder

from db.base.models import DemodData, Mode, Satellite, Telemetry, Transmitter

LOGGER = logging.getLogger('db')


def calculate_statistics():
    """Calculates statistics about the data we have in DB

    :returns: a dictionary of statistics
    """
    # satellite statistics
    satellites = Satellite.objects.all()
    total_satellites = satellites.count()

    # data statistics
    total_data = DemodData.objects.all().count()

    # transmitter statistics
    transmitters, total_transmitters, alive_transmitters_percentage = \
        calculate_transmitters_stats()

    # mode statistics
    mode_data_sorted, mode_label_sorted = \
        calculate_mode_stats(transmitters)

    # band statistics
    band_label_sorted, band_data_sorted = \
        calculate_band_stats(transmitters)

    statistics = {
        'total_satellites': total_satellites,
        'total_data': total_data,
        'transmitters': total_transmitters,
        'transmitters_alive': alive_transmitters_percentage,
        'mode_label': mode_label_sorted,
        'mode_data': mode_data_sorted,
        'band_label': band_label_sorted,
        'band_data': band_data_sorted
    }
    return statistics


def calculate_transmitters_stats():
    """Helper function to provite transmitters and statistics about
    transmitters in db (such as total and percentage of alive)"""
    transmitters = Transmitter.objects.all()
    total_transmitters = transmitters.count()
    # Remove the following pylint disable after Python 3 migration
    alive_transmitters = transmitters.filter(status='active').count()  # pylint: disable=E1101
    if alive_transmitters > 0 and total_transmitters > 0:
        try:
            alive_transmitters_percentage = '{0}%'.format(
                round((float(alive_transmitters) / float(total_transmitters)) * 100, 2)
            )
        except ZeroDivisionError as error:
            LOGGER.error(error, exc_info=True)
            alive_transmitters_percentage = '0%'
    else:
        alive_transmitters_percentage = '0%'

    return transmitters, total_transmitters, alive_transmitters_percentage


def calculate_mode_stats(transmitters):
    """Helper function to provide data and labels for modes associated with
    transmitters provided"""
    modes = Mode.objects.all()
    mode_label = []
    mode_data = []

    for mode in modes:
        filtered_transmitters = transmitters.filter(
            downlink_mode=mode
        ).count() + transmitters.filter(uplink_mode=mode).count()
        mode_label.append(mode.name)
        mode_data.append(filtered_transmitters)

    # needed to pass testing in a fresh environment with no modes in db
    if not mode_label:
        mode_label = ['FM']
    if not mode_data:
        mode_data = ['FM']

    mode_data_sorted, mode_label_sorted = \
        list(zip(*sorted(zip(mode_data, mode_label), reverse=True)))

    return mode_data_sorted, mode_label_sorted


def calculate_band_stats(transmitters):
    """Helper function to provide data and labels for bands associated with
    transmitters provided"""
    band_label = []
    band_data = []

    bands = [
        # <30.000.000 - HF
        {
            'lower_limit': 0,
            'upper_limit': 30000000,
            'label': 'HF'
        },
        # 30.000.000 ~ 300.000.000 - VHF
        {
            'lower_limit': 30000000,
            'upper_limit': 300000000,
            'label': 'VHF'
        },
        # 300.000.000 ~ 1.000.000.000 - UHF
        {
            'lower_limit': 300000000,
            'upper_limit': 1000000000,
            'label': 'UHF',
        },
        # 1G ~ 2G - L
        {
            'lower_limit': 1000000000,
            'upper_limit': 2000000000,
            'label': 'L',
        },
        # 2G ~ 4G - S
        {
            'lower_limit': 2000000000,
            'upper_limit': 4000000000,
            'label': 'S',
        },
        # 4G ~ 8G - C
        {
            'lower_limit': 4000000000,
            'upper_limit': 8000000000,
            'label': 'C',
        },
        # 8G ~ 12G - X
        {
            'lower_limit': 8000000000,
            'upper_limit': 12000000000,
            'label': 'X',
        },
        # 12G ~ 18G - Ku
        {
            'lower_limit': 12000000000,
            'upper_limit': 18000000000,
            'label': 'Ku',
        },
        # 18G ~ 27G - K
        {
            'lower_limit': 18000000000,
            'upper_limit': 27000000000,
            'label': 'K',
        },
        # 27G ~ 40G - Ka
        {
            'lower_limit': 27000000000,
            'upper_limit': 40000000000,
            'label': 'Ka',
        },
    ]

    for band in bands:
        filtered = transmitters.filter(
            downlink_low__gte=band['lower_limit'], downlink_low__lt=band['upper_limit']
        ).count()
        band_label.append(band['label'])
        band_data.append(filtered)

    band_data_sorted, band_label_sorted = \
        list(zip(*sorted(zip(band_data, band_label), reverse=True)))

    return band_label_sorted, band_data_sorted


def create_point(fields, satellite, telemetry, demoddata, version):
    """Create a decoded data point in JSON format that is influxdb compatible

    :returns: a JSON formatted time series data point
    """
    point = [
        {
            'time': demoddata.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'measurement': satellite.norad_cat_id,
            'tags': {
                'satellite': satellite.name,
                'decoder': telemetry.decoder,
                'station': demoddata.station,
                'observer': demoddata.observer,
                'source': demoddata.app_source,
                'version': version
            },
            'fields': fields
        }
    ]

    return point


def write_influx(json_obj):
    """Take a json object and send to influxdb."""
    client = InfluxDBClient(
        settings.INFLUX_HOST,
        settings.INFLUX_PORT,
        settings.INFLUX_USER,
        settings.INFLUX_PASS,
        settings.INFLUX_DB,
        ssl=settings.INFLUX_SSL,
        verify_ssl=settings.INFLUX_VERIFY_SSL
    )
    client.write_points(json_obj)


def decode_data(norad, period=None):
    """Decode data for a satellite, with an option to limit the scope.

    :param norad: the NORAD ID of the satellite to decode data for
    :param period: if period exists, only attempt to decode the last 4 hours,
    otherwise attempt to decode everything
    """
    sat = Satellite.objects.get(norad_cat_id=norad)
    if not sat.telemetry_decoder_count:
        return

    if period:
        time_period = datetime.utcnow() - timedelta(hours=4)
        time_period = make_aware(time_period)
        data = DemodData.objects.filter(satellite__norad_cat_id=norad, timestamp__gte=time_period)
    else:
        data = DemodData.objects.filter(satellite=sat)
    telemetry_decoders = Telemetry.objects.filter(satellite=sat)

    # iterate over DemodData objects
    for obj in data:
        # iterate over Telemetry decoders
        for tlmdecoder in telemetry_decoders:
            try:
                decoder_class = getattr(decoder, tlmdecoder.decoder.capitalize())
            except AttributeError:
                continue
            try:
                with open(obj.payload_frame.path) as frame_file:
                    # we get data frames in hex but kaitai requires binary
                    hexdata = frame_file.read()
                    bindata = binascii.unhexlify(hexdata)

                # if we are set to use InfluxDB, send the decoded data
                # there, otherwise we store it in the local DB.
                if settings.USE_INFLUX:
                    try:
                        frame = decoder_class.from_bytes(bindata)
                        json_obj = create_point(
                            decoder.get_fields(frame), sat, tlmdecoder, obj, decoders_version
                        )
                        write_influx(json_obj)
                        obj.payload_decoded = 'influxdb'
                        obj.is_decoded = True
                        obj.save()
                        break
                    except Exception:  # pylint: disable=W0703
                        obj.is_decoded = False
                        obj.save()
                        continue
                else:  # store in the local db instead of influx
                    try:
                        frame = decoder_class.from_bytes(bindata)
                    except Exception:  # pylint: disable=W0703
                        obj.payload_decoded = ''
                        obj.is_decoded = False
                        obj.save()
                        continue
                    else:
                        json_obj = create_point(
                            decoder.get_fields(frame), sat, tlmdecoder, obj, decoders_version
                        )
                        obj.payload_decoded = json_obj
                        obj.is_decoded = True
                        obj.save()
                        break
            except (IOError, binascii.Error) as error:
                LOGGER.error(error, exc_info=True)
                continue


# Caches stats about satellites and data
def cache_statistics():
    """Populate a django cache with statistics from data in DB

    .. seealso:: calculate_statistics
    """
    statistics = calculate_statistics()
    cache.set('stats_transmitters', statistics, 60 * 60 * 2)

    ids = Satellite.objects.values('id')
    cache.set('satellites_ids', ids, 60 * 60 * 2)

    satellites = Satellite.objects \
                          .values('name', 'norad_cat_id', 'id') \
                          .annotate(count=Count('telemetry_data'),
                                    latest_payload=Max('telemetry_data__timestamp')) \
                          .order_by('-count')

    for sat in satellites:
        cache.set(sat['id'], sat, 60 * 60 * 2)

    observers = DemodData.objects \
                         .values('observer') \
                         .annotate(count=Count('observer'),
                                   latest_payload=Max('timestamp')) \
                         .order_by('-count')
    cache.set('stats_observers', observers, 60 * 60 * 2)


def remove_exponent(converted_number):
    """Remove exponent."""
    return converted_number.quantize(
        Decimal(1)
    ) if converted_number == converted_number.to_integral() else converted_number.normalize()


def millify(number, precision=0):
    """Humanize number."""
    millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
    number = float(number)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if number == 0 else math.log10(abs(number)) / 3))
        )
    )
    result = '{:.{precision}f}'.format(number / 10**(3 * millidx), precision=precision)
    result = remove_exponent(Decimal(result))
    return '{0}{dx}'.format(result, dx=millnames[millidx])


def read_influx(norad):
    """Queries influxdb for the last 30d of data points (counted) in 1d resolution.

    :param norad: the NORAD ID of the satellite to query influxdb for
    :returns: a raw json of the measurement, timestamps, and point counts
    """
    client = InfluxDBClient(
        settings.INFLUX_HOST,
        settings.INFLUX_PORT,
        settings.INFLUX_USER,
        settings.INFLUX_PASS,
        settings.INFLUX_DB,
        ssl=settings.INFLUX_SSL,
        verify_ssl=settings.INFLUX_VERIFY_SSL
    )

    # check against injection
    if isinstance(norad, int):
        # epoch:s to set the return timestamp in unixtime for easier conversion
        params = {'epoch': 's'}
        results = client.query(
            'SELECT count(*) FROM "' + str(norad) +
            '" WHERE time > now() - 30d GROUP BY time(1d) fill(null)',
            params=params
        )
        return results.raw
    # no-else-return
    return ''
