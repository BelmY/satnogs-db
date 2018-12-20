import logging
import binascii

from datetime import datetime, timedelta
from db.base.models import Satellite, Transmitter, Mode, DemodData, Telemetry
from django.conf import settings
from django.utils.timezone import make_aware
from influxdb import InfluxDBClient
from satnogsdecoders import decoder

logger = logging.getLogger('db')


def calculate_statistics():
    """View to create statistics endpoint."""
    satellites = Satellite.objects.all()
    transmitters = Transmitter.objects.all()
    modes = Mode.objects.all()

    total_satellites = satellites.count()
    total_transmitters = transmitters.count()
    total_data = DemodData.objects.all().count()
    alive_transmitters = transmitters.filter(alive=True).count()
    try:
        alive_transmitters_percentage = '{0}%'.format(round((float(alive_transmitters) /
                                                             float(total_transmitters)) * 100, 2))
    except ZeroDivisionError as error:
        logger.error(error, exc_info=True)
        alive_transmitters_percentage = '0%'

    mode_label = []
    mode_data = []
    for mode in modes:
        tr = transmitters.filter(mode=mode).count()
        mode_label.append(mode.name)
        mode_data.append(tr)

    band_label = []
    band_data = []

    # <30.000.000 - HF
    filtered = transmitters.filter(downlink_low__lt=30000000).count()
    band_label.append('HF')
    band_data.append(filtered)

    # 30.000.000 ~ 300.000.000 - VHF
    filtered = transmitters.filter(downlink_low__gte=30000000,
                                   downlink_low__lt=300000000).count()
    band_label.append('VHF')
    band_data.append(filtered)

    # 300.000.000 ~ 1.000.000.000 - UHF
    filtered = transmitters.filter(downlink_low__gte=300000000,
                                   downlink_low__lt=1000000000).count()
    band_label.append('UHF')
    band_data.append(filtered)

    # 1G ~ 2G - L
    filtered = transmitters.filter(downlink_low__gte=1000000000,
                                   downlink_low__lt=2000000000).count()
    band_label.append('L')
    band_data.append(filtered)

    # 2G ~ 4G - S
    filtered = transmitters.filter(downlink_low__gte=2000000000,
                                   downlink_low__lt=4000000000).count()
    band_label.append('S')
    band_data.append(filtered)

    # 4G ~ 8G - C
    filtered = transmitters.filter(downlink_low__gte=4000000000,
                                   downlink_low__lt=8000000000).count()
    band_label.append('C')
    band_data.append(filtered)

    # 8G ~ 12G - X
    filtered = transmitters.filter(downlink_low__gte=8000000000,
                                   downlink_low__lt=12000000000).count()
    band_label.append('X')
    band_data.append(filtered)

    # 12G ~ 18G - Ku
    filtered = transmitters.filter(downlink_low__gte=12000000000,
                                   downlink_low__lt=18000000000).count()
    band_label.append('Ku')
    band_data.append(filtered)

    # 18G ~ 27G - K
    filtered = transmitters.filter(downlink_low__gte=18000000000,
                                   downlink_low__lt=27000000000).count()
    band_label.append('K')
    band_data.append(filtered)

    # 27G ~ 40G - Ka
    filtered = transmitters.filter(downlink_low__gte=27000000000,
                                   downlink_low__lt=40000000000).count()
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


# kaitai does not give us a good way to export attributes when we don't know
# what those attributes are, and here we are dealing with a lot of various
# decoders with different attributes. This is a hacky way of getting them
# to json. We also need to sanitize this for any binary data left over as
# it won't export to json.

def kaitai_to_json(structdict, satellite, telemetry, demoddata, json_obj):
    """Recursively sends dict string/int data to the given json_obj"""
    for key, value in structdict.iteritems():
        if type(value) is dict:  # recursion
            kaitai_to_json(value, satellite, telemetry, demoddata, json_obj)
        else:
            data = {
                'time': demoddata.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'measurement': key,
                'tags': {
                    'satellite': satellite.name,
                    'norad': satellite.norad_cat_id,
                    'decoder': telemetry.decoder,
                    'station': demoddata.station,
                    'observer': demoddata.observer,
                    'source': demoddata.source
                }
            }
            if isinstance(value, basestring):  # skip binary values
                try:
                    value.decode('utf-8')
                    data.update({'fields': {'value': value}})
                except UnicodeError:
                    continue
            else:
                data.update({'fields': {'value': value}})
            if 'value' in data['fields']:
                json_obj.append(data)


def kaitai_to_dict(struct):
    """Take a kaitai decode object and return a dict object"""
    structdict = struct.__dict__
    todict = {}
    for key, value in structdict.iteritems():
        if not key.startswith("_"):  # kaitai objects and priv vars, skip
            if isinstance(value, basestring):  # skip binary values
                try:
                    value.decode('utf-8')
                    todict[key] = value
                except UnicodeError:
                    continue
            elif hasattr(value, '__dict__'):
                todict[key] = kaitai_to_dict(value)  # recursion
            else:
                todict[key] = value
    return todict


def write_influx(json_obj):
    """Take a json object and send to influxdb."""
    client = InfluxDBClient(settings.INFLUX_HOST, settings.INFLUX_PORT,
                            settings.INFLUX_USER, settings.INFLUX_PASS,
                            settings.INFLUX_DB, ssl=settings.INFLUX_SSL)
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
                    decoder_class = getattr(decoder,
                                            tlmdecoder.decoder.capitalize())
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
                            json_obj = []
                            kaitai_to_json(kaitai_to_dict(frame), sat,
                                           tlmdecoder, obj, json_obj)
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
                            json_obj = []
                            kaitai_to_json(kaitai_to_dict(frame), sat,
                                           tlmdecoder, obj, json_obj)
                            obj.payload_decoded = json_obj
                            obj.is_decoded = True
                            obj.save()
                            break
                except IOError:
                    continue
