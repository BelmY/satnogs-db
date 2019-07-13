"""SatNOGS DB django management command to fetch data (TLEs, etc)"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from pytz import timezone

from db.base.models import DemodData, Satellite, TransmitterEntry


class Command(BaseCommand):
    """django management command to fetch data (TLEs, etc)"""
    help = 'Fetch Satellite data from Network'

    def handle(self, *args, **options):
        apiurl = settings.NETWORK_API_ENDPOINT
        data_url = "{0}data".format(apiurl)
        start_date = datetime.utcnow() - timedelta(days=int(settings.DATA_FETCH_DAYS))
        start_date = datetime.strftime(start_date, '%Y-%m-%dT%H:%M:%SZ')
        params = {'start': start_date}
        response = requests.get(data_url, params=params)

        satellites = Satellite.objects.all()

        for obj in response.json():
            norad_cat_id = obj['norad_cat_id']
            data_id = obj['id']
            station = obj['station_name']
            lat = obj['station_lat']
            lng = obj['station_lng']
            try:
                satellite = satellites.get(norad_cat_id=norad_cat_id)
            except Satellite.DoesNotExist:
                continue
            try:
                transmitter = TransmitterEntry.objects.get(
                    uuid=obj['transmitter'], created=obj['transmitter_created']
                )
            except TransmitterEntry.DoesNotExist:
                transmitter = None

            DemodData.objects.filter(data_id=data_id).delete()

            for demoddata in obj['demoddata']:
                payload_url = demoddata['payload_demod']
                timestamp = datetime.strptime(
                    payload_url.split('/')[-1].split('_')[0], '%Y%m%dT%H%M%SZ'
                ).replace(tzinfo=timezone('UTC'))
                frame = str(requests.get(payload_url).json())
                payload_frame = ContentFile(frame, name='network')

                DemodData.objects.create(
                    satellite=satellite,
                    transmitter=transmitter,
                    data_id=data_id,
                    payload_frame=payload_frame,
                    timestamp=timestamp,
                    source='network',
                    station=station,
                    lat=lat,
                    lng=lng
                )
