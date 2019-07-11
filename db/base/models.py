from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json
import logging
from os import path
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import OuterRef, Subquery
from django.db.models.signals import post_save, pre_save
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from markdown import markdown
from shortuuidfield import ShortUUIDField

from db.base.helpers import gridsquare

LOGGER = logging.getLogger('db')

DATA_SOURCES = ['manual', 'network', 'sids']
SATELLITE_STATUS = ['alive', 'dead', 're-entered']
TRANSMITTER_STATUS = ['active', 'inactive', 'invalid']
TRANSMITTER_TYPE = ['Transmitter', 'Transceiver', 'Transponder']
SERVICE_TYPE = [
    'Aeronautical', 'Amateur', 'Broadcasting', 'Earth Exploration', 'Fixed', 'Inter-satellite',
    'Maritime', 'Meteorological', 'Mobile', 'Radiolocation', 'Radionavigational',
    'Space Operation', 'Space Research', 'Standard Frequency and Time Signal', 'Unknown'
]


def _name_payload_frame(instance, filename):
    today = now()
    folder = 'payload_frames/{0}/{1}/{2}/'.format(today.year, today.month, today.day)
    ext = 'raw'
    filename = '{0}_{1}.{2}'.format(filename, uuid4().hex, ext)
    return path.join(folder, filename)


def _gen_observer(sender, instance, created, **kwargs):
    post_save.disconnect(_gen_observer, sender=DemodData)
    try:
        qth = gridsquare(instance.lat, instance.lng)
    except Exception:
        instance.observer = 'Unknown'
    else:
        instance.observer = '{0}-{1}'.format(instance.station, qth)
    instance.save()
    post_save.connect(_gen_observer, sender=DemodData)


def _set_is_decoded(sender, instance, **kwargs):
    instance.is_decoded = instance.payload_decoded != ''


@python_2_unicode_compatible
class Mode(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Satellite(models.Model):
    """Model for all the satellites."""
    norad_cat_id = models.PositiveIntegerField()
    name = models.CharField(max_length=45)
    names = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='satellites', blank=True, help_text='Ideally: 250x250')
    tle1 = models.CharField(max_length=200, blank=True)
    tle2 = models.CharField(max_length=200, blank=True)
    tle_source = models.CharField(max_length=300, blank=True)
    status = models.CharField(
        choices=list(zip(SATELLITE_STATUS, SATELLITE_STATUS)), max_length=10, default='alive'
    )
    decayed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['norad_cat_id']

    def get_description(self):
        return markdown(self.description)

    def get_image(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return settings.SATELLITE_DEFAULT_IMAGE

    @property
    def transmitters(self):
        return Transmitter.objects.filter(satellite=self.id).exclude(status='invalid')

    @property
    def pending_transmitter_suggestions(self):
        pending = TransmitterSuggestion.objects.filter(satellite=self.id).count()
        return pending

    @property
    def has_telemetry_data(self):
        has_data = DemodData.objects.filter(satellite=self.id).count()
        return has_data

    @property
    def has_telemetry_decoders(self):
        has_decoders = Telemetry.objects.filter(satellite=self.id).exclude(decoder='').count()
        return has_decoders

    def __str__(self):
        return '{0} - {1}'.format(self.norad_cat_id, self.name)


@python_2_unicode_compatible
class TransmitterEntry(models.Model):
    """Model for satellite transmitters."""
    uuid = ShortUUIDField(db_index=True)
    description = models.TextField()
    status = models.CharField(
        choices=list(zip(TRANSMITTER_STATUS, TRANSMITTER_STATUS)), max_length=8, default='active'
    )
    type = models.CharField(
        choices=list(zip(TRANSMITTER_TYPE, TRANSMITTER_TYPE)),
        max_length=11,
        default='Transmitter'
    )
    uplink_low = models.BigIntegerField(blank=True, null=True)
    uplink_high = models.BigIntegerField(blank=True, null=True)
    uplink_drift = models.IntegerField(blank=True, null=True)
    downlink_low = models.BigIntegerField(blank=True, null=True)
    downlink_high = models.BigIntegerField(blank=True, null=True)
    downlink_drift = models.IntegerField(blank=True, null=True)
    mode = models.ForeignKey(
        Mode, blank=True, null=True, on_delete=models.SET_NULL, related_name='transmitter_entries'
    )
    invert = models.BooleanField(default=False)
    baud = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    satellite = models.ForeignKey(
        Satellite, null=True, related_name='transmitter_entries', on_delete=models.SET_NULL
    )
    reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(default=now)
    citation = models.CharField(max_length=512, default='CITATION NEEDED - https://xkcd.com/285/')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    service = models.CharField(
        choices=zip(SERVICE_TYPE, SERVICE_TYPE), max_length=34, default='Unknown'
    )

    class Meta:
        unique_together = ("uuid", "created")
        verbose_name_plural = 'Transmitter entries'

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        self.id = None  # pylint: disable=C0103
        super(TransmitterEntry, self).save()


class TransmitterSuggestionManager(models.Manager):
    def get_queryset(self):
        return TransmitterEntry.objects.filter(reviewed=False)


class TransmitterSuggestion(TransmitterEntry):
    objects = TransmitterSuggestionManager()

    class Meta:
        proxy = True
        permissions = (('approve', 'Can approve/reject transmitter suggestions'), )


class TransmitterManager(models.Manager):
    def get_queryset(self):
        subquery = TransmitterEntry.objects.filter(
            reviewed=True, approved=True
        ).filter(uuid=OuterRef('uuid')).order_by('-created')
        return super(TransmitterManager, self).get_queryset().filter(
            reviewed=True, approved=True
        ).filter(created=Subquery(subquery.values('created')[:1]))


class Transmitter(TransmitterEntry):
    objects = TransmitterManager()

    class Meta:
        proxy = True


@python_2_unicode_compatible
class Telemetry(models.Model):
    """Model for satellite telemtry decoders."""
    satellite = models.ForeignKey(
        Satellite, null=True, related_name='telemetries', on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=45)
    schema = models.TextField(blank=True)
    decoder = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['satellite__norad_cat_id']
        verbose_name_plural = 'Telemetries'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class DemodData(models.Model):
    """Model for satellite for observation data."""
    satellite = models.ForeignKey(
        Satellite, null=True, related_name='telemetry_data', on_delete=models.SET_NULL
    )
    transmitter = models.ForeignKey(
        TransmitterEntry, null=True, blank=True, on_delete=models.SET_NULL
    )
    app_source = models.CharField(
        choices=list(zip(DATA_SOURCES, DATA_SOURCES)), max_length=7, default='sids'
    )
    data_id = models.PositiveIntegerField(blank=True, null=True)
    payload_frame = models.FileField(upload_to=_name_payload_frame, blank=True, null=True)
    payload_decoded = models.TextField(blank=True)
    payload_telemetry = models.ForeignKey(
        Telemetry, null=True, blank=True, on_delete=models.SET_NULL
    )
    station = models.CharField(max_length=45, default='Unknown')
    observer = models.CharField(max_length=60, blank=True)
    lat = models.FloatField(validators=[MaxValueValidator(90), MinValueValidator(-90)], default=0)
    lng = models.FloatField(
        validators=[MaxValueValidator(180), MinValueValidator(-180)], default=0
    )
    is_decoded = models.BooleanField(default=False, db_index=True)
    timestamp = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return 'data-for-{0}'.format(self.satellite.norad_cat_id)

    def display_decoded(self):
        try:
            json.dumps(self.payload_decoded)
        except Exception:
            '{}'

    def display_frame(self):
        try:
            with open(self.payload_frame.path) as frame_file:
                return frame_file.read()
        except IOError as err:
            LOGGER.error(
                err, exc_info=True, extra={
                    'payload frame path': self.payload_frame.path,
                }
            )
            return None


post_save.connect(_gen_observer, sender=DemodData)
pre_save.connect(_set_is_decoded, sender=DemodData)
