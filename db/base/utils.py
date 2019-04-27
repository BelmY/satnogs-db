import logging
import binascii

from datetime import datetime, timedelta
from db.base.models import Satellite, Transmitter, Mode, DemodData, Telemetry
from django.db.models import Count, Max
from django.conf import settings
from django.utils.timezone import make_aware
from influxdb import InfluxDBClient
from satnogsdecoders import decoder
from django.core.cache import cache

logger = logging.getLogger('db')


def calculate_statistics():
    """View to create statistics endpoint."""
    satellites = Satellite.objects.all()
    transmitters = Transmitter.objects.all()
    modes = Mode.objects.all()

    total_satellites = satellites.count()
    total_transmitters = transmitters.count()
    total_data = DemodData.objects.all().count()
    alive_transmitters = transmitters.filter(status='active').count()
    if alive_transmitters > 0 and total_transmitters > 0:
        try:
            alive_transmitters_percentage = '{0}%'.format(
                round((float(alive_transmitters) / float(total_transmitters)) * 100, 2)
            )
        except ZeroDivisionError as error:
            logger.error(error, exc_info=True)
            alive_transmitters_percentage = '0%'
    else:
        alive_transmitters_percentage = '0%'

    mode_label = []
    mode_data = []
    for mode in modes:
        tr = transmitters.filter(mode=mode).count()
        mode_label.append(mode.name)
        mode_data.append(tr)

    # needed to pass testing in a fresh environment with no modes in db
    if len(mode_label) == 0:
        mode_label = ['FM']
    if len(mode_data) == 0:
        mode_data = ['FM']

    band_label = []
    band_data = []

    # <30.000.000 - HF
    filtered = transmitters.filter(downlink_low__lt=30000000).count()
    band_label.append('HF')
    band_data.append(filtered)

    # 30.000.000 ~ 300.000.000 - VHF
    filtered = transmitters.filter(downlink_low__gte=30000000, downlink_low__lt=300000000).count()
    band_label.append('VHF')
    band_data.append(filtered)

    # 300.000.000 ~ 1.000.000.000 - UHF
    filtered = transmitters.filter(
        downlink_low__gte=300000000, downlink_low__lt=1000000000
    ).count()
    band_label.append('UHF')
    band_data.append(filtered)

    # 1G ~ 2G - L
    filtered = transmitters.filter(
        downlink_low__gte=1000000000, downlink_low__lt=2000000000
    ).count()
    band_label.append('L')
    band_data.append(filtered)

    # 2G ~ 4G - S
    filtered = transmitters.filter(
        downlink_low__gte=2000000000, downlink_low__lt=4000000000
    ).count()
    band_label.append('S')
    band_data.append(filtered)

    # 4G ~ 8G - C
    filtered = transmitters.filter(
        downlink_low__gte=4000000000, downlink_low__lt=8000000000
    ).count()
    band_label.append('C')
    band_data.append(filtered)

    # 8G ~ 12G - X
    filtered = transmitters.filter(
        downlink_low__gte=8000000000, downlink_low__lt=12000000000
    ).count()
    band_label.append('X')
    band_data.append(filtered)

    # 12G ~ 18G - Ku
    filtered = transmitters.filter(
        downlink_low__gte=12000000000, downlink_low__lt=18000000000
    ).count()
    band_label.append('Ku')
    band_data.append(filtered)

    # 18G ~ 27G - K
    filtered = transmitters.filter(
        downlink_low__gte=18000000000, downlink_low__lt=27000000000
    ).count()
    band_label.append('K')
    band_data.append(filtered)

    # 27G ~ 40G - Ka
    filtered = transmitters.filter(
        downlink_low__gte=27000000000, downlink_low__lt=40000000000
    ).count()
    band_label.append('Ka')
    band_data.append(filtered)

    mode_data_sorted, mode_label_sorted = zip(*sorted(zip(mode_data, mode_label), reverse=True))
    band_data_sorted, band_label_sorted = zip(*sorted(zip(band_data, band_label), reverse=True))

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


def create_point(fields, satellite, telemetry, demoddata):
    """Create a decoded data point"""
    point = [
        {
            'time': demoddata.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'measurement': satellite.norad_cat_id,
            'tags': {
                'satellite': satellite.name,
                'decoder': telemetry.decoder,
                'station': demoddata.station,
                'observer': demoddata.observer,
                'source': demoddata.app_source
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
        ssl=settings.INFLUX_SSL
    )
    client.write_points(json_obj)


def decode_data(norad, period=None):
    """Decode data for a satellite, with an option to limit the scope."""
    sat = Satellite.objects.get(norad_cat_id=norad)
    if sat.has_telemetry_decoders:
        now = datetime.utcnow()
        if period:
            q = now - timedelta(hours=4)
            q = make_aware(q)
            data = DemodData.objects.filter(satellite__norad_cat_id=norad,
                                            timestamp__gte=q) \
                                    .filter(is_decoded=False)
        else:
            data = DemodData.objects.filter(satellite=sat) \
                                    .filter(is_decoded=False)
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
                    with open(obj.payload_frame.path) as fp:
                        # we get data frames in hex but kaitai requires binary
                        hexdata = fp.read()
                        bindata = binascii.unhexlify(hexdata)

                    # if we are set to use InfluxDB, send the decoded data
                    # there, otherwise we store it in the local DB.
                    if settings.USE_INFLUX:
                        try:
                            frame = decoder_class.from_bytes(bindata)
                            json_obj = create_point(
                                decoder.get_fields(frame), sat, tlmdecoder, obj
                            )
                            write_influx(json_obj)
                            obj.payload_decoded = 'influxdb'
                            obj.is_decoded = True
                            obj.save()
                            break
                        except Exception:
                            obj.is_decoded = False
                            obj.save()
                            continue
                    else:  # store in the local db instead of influx
                        try:
                            frame = decoder_class.from_bytes(bindata)
                        except Exception:
                            obj.payload_decoded = ''
                            obj.is_decoded = False
                            obj.save()
                            continue
                        else:
                            json_obj = create_point(
                                decoder.get_fields(frame), sat, tlmdecoder, obj
                            )
                            obj.payload_decoded = json_obj
                            obj.is_decoded = True
                            obj.save()
                            break
                except IOError:
                    continue


# Caches stats about satellites and data
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
