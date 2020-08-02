"""Django database model for SatNOGS DB"""
import logging
from os import path
from uuid import uuid4

import h5py
import satnogsdecoders
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, \
    URLValidator
from django.db import models
from django.db.models import OuterRef, Subquery
from django.db.models.signals import post_save, pre_save
from django.utils.timezone import now
from django_countries.fields import CountryField
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
URL_REGEX = r"(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
MIN_FREQ = 0
MAX_FREQ = 40000000000
MIN_FREQ_MSG = "Ensure this value is greater than or equal to 0Hz"
MAX_FREQ_MSG = "Ensure this value is less than or equal to 40Ghz"


def _name_exported_frames(instance, filename):  # pylint: disable=W0613
    """Returns path for a exported frames file"""
    return path.join('download/', filename)


def _name_payload_frame(instance, filename):  # pylint: disable=W0613
    """Returns a unique, timestamped path and filename for a payload

    :param filename: the original filename submitted
    :returns: path string with timestamped subfolders and filename
    """
    today = now()
    folder = 'payload_frames/{0}/{1}/{2}/'.format(today.year, today.month, today.day)
    ext = 'raw'
    filename = '{0}_{1}.{2}'.format(filename, uuid4().hex, ext)
    return path.join(folder, filename)


def _gen_observer(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_gen_observer, sender=DemodData)
    try:
        qth = gridsquare(instance.lat, instance.lng)
    except Exception:  # pylint: disable=W0703
        instance.observer = 'Unknown'
    else:
        instance.observer = '{0}-{1}'.format(instance.station, qth)
    instance.save()
    post_save.connect(_gen_observer, sender=DemodData)


def _set_is_decoded(sender, instance, **kwargs):  # pylint: disable=W0613
    """Returns true if payload_decoded has data"""
    instance.is_decoded = instance.payload_decoded != ''


def _extract_network_obs_id(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_extract_network_obs_id, sender=Artifact)
    try:
        with h5py.File(instance.artifact_file, 'r') as h5_file:
            instance.network_obs_id = h5_file.attrs["observation_id"]
    except OSError as error:
        LOGGER.warning(error)

    instance.save()
    post_save.connect(_extract_network_obs_id, sender=Artifact)


class Mode(models.Model):
    """A satellite transmitter RF mode. For example: FM"""
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name


class Operator(models.Model):
    """Satellite Owner/Operator"""
    name = models.CharField(max_length=255, unique=True)
    names = models.TextField(blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(
        blank=True, validators=[URLValidator(schemes=['http', 'https'], regex=URL_REGEX)]
    )

    def __str__(self):
        return self.name


class Satellite(models.Model):
    """Model for all the satellites."""
    norad_cat_id = models.PositiveIntegerField()
    name = models.CharField(max_length=45)
    names = models.TextField(blank=True)
    description = models.TextField(blank=True)
    dashboard_url = models.URLField(
        blank=True,
        null=True,
        max_length=200,
        validators=[URLValidator(schemes=['http', 'https'], regex=URL_REGEX)]
    )
    image = models.ImageField(upload_to='satellites', blank=True, help_text='Ideally: 250x250')
    tle1 = models.CharField(max_length=200, blank=True)
    tle2 = models.CharField(max_length=200, blank=True)
    tle_source = models.CharField(max_length=300, blank=True)
    status = models.CharField(
        choices=list(zip(SATELLITE_STATUS, SATELLITE_STATUS)), max_length=10, default='alive'
    )
    decayed = models.DateTimeField(null=True, blank=True)

    # new fields below, metasat etc
    # countries is multiple for edge cases like ISS/Zarya
    countries = CountryField(blank=True, multiple=True, blank_label='(select countries)')
    website = models.URLField(
        blank=True, validators=[URLValidator(schemes=['http', 'https'], regex=URL_REGEX)]
    )
    launched = models.DateTimeField(null=True, blank=True)
    deployed = models.DateTimeField(null=True, blank=True)
    operator = models.ForeignKey(
        Operator,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='satellite_operator'
    )

    class Meta:
        ordering = ['norad_cat_id']

    def get_description(self):
        """Returns the markdown-processed satellite description

        :returns: the markdown-processed satellite description
        """
        return markdown(self.description)

    def get_image(self):
        """Returns an image for the satellite

        :returns: the saved image for the satellite, or a default
        """
        if self.image and hasattr(self.image, 'url'):
            image = self.image.url
        else:
            image = settings.SATELLITE_DEFAULT_IMAGE
        return image

    @property
    def transmitters(self):
        """Returns valid transmitters for this Satellite

        :returns: the valid transmitters for this Satellite
        """
        transmitters = Transmitter.objects.filter(satellite=self.id)
        return transmitters.exclude(status='invalid')

    @property
    def transmitter_suggestion_count(self):
        """Returns number of pending transmitter suggestions for this Satellite

        :returns: number of pending transmitter suggestions for this Satellite
        """
        pending_count = TransmitterSuggestion.objects.filter(satellite=self.id).count()
        return pending_count

    @property
    def telemetry_data_count(self):
        """Returns number of DemodData for this Satellite

        :returns: number of DemodData for this Satellite
        """
        data_count = DemodData.objects.filter(satellite=self.id).count()
        return data_count

    @property
    def telemetry_decoder_count(self):
        """Returns number of Telemetry objects for this Satellite

        :returns: number of Telemetry objects for this Satellite
        """
        decoder_count = Telemetry.objects.filter(satellite=self.id).exclude(decoder='').count()
        return decoder_count

    @property
    def transmitter_count(self):
        """Returns number of approved transmitter suggestions for this Satellite

        :returns: number of approved transmitter suggestions for this Satellite
        """
        approved_count = Transmitter.objects.filter(satellite=self.id).count()
        return approved_count

    @property
    def tle_redistributable(self):
        """Returns True if re-distribution of the TLE is allowed, False otherwise

        :returns: True if re-distribution of the TLE is allowed, False otherwise
        """
        return self.tle_source in settings.TLE_SOURCES_REDISTRIBUTABLE

    @property
    def latest_tle(self):
        """Returns the latest TLE for this Satellite

        :returns: dict with the latest TLE, it's source and whether redistribution is allowed
        """
        return {
            'source': self.tle_source,
            'norad_cat_id': self.norad_cat_id,
            'tle1': self.tle1,
            'tle2': self.tle2,
            'redistributable': self.tle_redistributable
        }

    @property
    def latest_data(self):
        """Returns the latest DemodData for this Satellite

        :returns: dict with most recent DemodData for this Satellite
        """
        data = DemodData.objects.filter(satellite=self.id).order_by('-id')[:1]
        return {
            'data_id': data[0].data_id,
            'payload_frame': data[0].payload_frame,
            'timestamp': data[0].timestamp,
            'is_decoded': data[0].is_decoded,
            'station': data[0].station,
            'observer': data[0].observer,
        }

    @property
    def needs_help(self):
        """Returns a boolean based on whether or not this Satellite could
            use some editorial help based on a configurable threshold

        :returns: bool
        """
        score = 0
        if self.description and self.description != '':
            score += 1
        if self.countries and self.countries != '':
            score += 1
        if self.website and self.website != '':
            score += 1
        if self.names and self.names != '':
            score += 1
        if self.launched and self.launched != '':
            score += 1
        if self.operator and self.operator != '':
            score += 1
        if self.image and self.image != '':
            score += 1

        return score <= 2

    def __str__(self):
        return '{0} - {1}'.format(self.norad_cat_id, self.name)


class TransmitterEntry(models.Model):
    """Model for satellite transmitters."""
    uuid = ShortUUIDField(db_index=True)
    description = models.TextField(
        help_text='Short description for this entry, like: UHF 9k6 AFSK Telemetry'
    )
    status = models.CharField(
        choices=list(zip(TRANSMITTER_STATUS, TRANSMITTER_STATUS)),
        max_length=8,
        default='active',
        help_text='Functional state of this transmitter'
    )
    type = models.CharField(
        choices=list(zip(TRANSMITTER_TYPE, TRANSMITTER_TYPE)),
        max_length=11,
        default='Transmitter'
    )
    uplink_low = models.BigIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_FREQ, message=MIN_FREQ_MSG),
            MaxValueValidator(MAX_FREQ, message=MAX_FREQ_MSG)
        ],
        help_text='Frequency (in Hz) for the uplink, or bottom of the uplink range for a \
            transponder'
    )
    uplink_high = models.BigIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_FREQ, message=MIN_FREQ_MSG),
            MaxValueValidator(MAX_FREQ, message=MAX_FREQ_MSG)
        ],
        help_text='Frequency (in Hz) for the top of the uplink range for a transponder'
    )
    uplink_drift = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-99999), MaxValueValidator(99999)],
        help_text='Receiver drift from the published uplink frequency, stored in parts \
            per billion (PPB)'
    )
    downlink_low = models.BigIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_FREQ, message=MIN_FREQ_MSG),
            MaxValueValidator(MAX_FREQ, message=MAX_FREQ_MSG)
        ],
        help_text='Frequency (in Hz) for the downlink, or bottom of the downlink range \
            for a transponder'
    )
    downlink_high = models.BigIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_FREQ, message=MIN_FREQ_MSG),
            MaxValueValidator(MAX_FREQ, message=MAX_FREQ_MSG)
        ],
        help_text='Frequency (in Hz) for the top of the downlink range for a transponder'
    )
    downlink_drift = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(-99999), MaxValueValidator(99999)],
        help_text='Transmitter drift from the published downlink frequency, stored in \
            parts per billion (PPB)'
    )
    downlink_mode = models.ForeignKey(
        Mode,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transmitter_downlink_entries',
        help_text='Modulation mode for the downlink'
    )
    uplink_mode = models.ForeignKey(
        Mode,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='transmitter_uplink_entries',
        help_text='Modulation mode for the uplink'
    )
    invert = models.BooleanField(
        default=False, help_text='True if this is an inverted transponder'
    )
    baud = models.FloatField(
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text='The number of modulated symbols that the transmitter sends every second'
    )
    satellite = models.ForeignKey(
        Satellite, null=True, related_name='transmitter_entries', on_delete=models.SET_NULL
    )
    reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(default=now, help_text='Timestamp for this entry or edit')
    citation = models.CharField(
        max_length=512,
        default='CITATION NEEDED - https://xkcd.com/285/',
        help_text='A reference (preferrably URL) for this entry or edit'
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    service = models.CharField(
        choices=zip(SERVICE_TYPE, SERVICE_TYPE),
        max_length=34,
        default='Unknown',
        help_text='The published usage category for this transmitter'
    )

    # NOTE: future fields will need to be added to forms.py and to
    # api/serializers.py

    class Meta:
        unique_together = ("uuid", "created")
        verbose_name_plural = 'Transmitter entries'

    def __str__(self):
        return self.description

    # see https://github.com/PyCQA/pylint-django/issues/94 for why W0221
    def save(self, *args, **kwargs):  # pylint: disable=W0221
        # this assignment is needed to preserve changes made to a Transmitter
        # through the admin UI
        self.id = None  # pylint: disable=C0103, W0201
        super(TransmitterEntry, self).save()

    def clean(self):
        if self.type == TRANSMITTER_TYPE[0]:
            if self.uplink_low is not None or self.uplink_high is not None \
                    or self.uplink_drift is not None:
                raise ValidationError("Uplink shouldn't be filled in for a transmitter")

            if self.downlink_high:
                raise ValidationError(
                    "Downlink high frequency shouldn't be filled in for a transmitter"
                )

        elif self.type == TRANSMITTER_TYPE[1]:
            if self.uplink_high is not None or self.downlink_high is not None:
                raise ValidationError("Frequency range shouldn't be filled in for a transceiver")

        elif self.type == TRANSMITTER_TYPE[2]:
            if self.downlink_low is not None and self.downlink_high is not None:
                if self.downlink_low > self.downlink_high:
                    raise ValidationError(
                        "Downlink low frequency must be lower or equal \
                        than downlink high frequency"
                    )

            if self.uplink_low is not None and self.uplink_high is not None:
                if self.uplink_low > self.uplink_high:
                    raise ValidationError(
                        "Uplink low frequency must be lower or equal \
                        than uplink high frequency"
                    )


class TransmitterSuggestionManager(models.Manager):  # pylint: disable=R0903
    """Django Manager for TransmitterSuggestions

    TransmitterSuggestions are TransmitterEntry objects that have been
    submitted (suggested) but not yet reviewed
    """
    def get_queryset(self):  # pylint: disable=R0201
        """Returns TransmitterEntries that have not been reviewed"""
        return TransmitterEntry.objects.filter(reviewed=False)


class TransmitterSuggestion(TransmitterEntry):
    """TransmitterSuggestion is an unreviewed TransmitterEntry object"""
    objects = TransmitterSuggestionManager()

    def __str__(self):
        return self.description

    class Meta:
        proxy = True
        permissions = (('approve', 'Can approve/reject transmitter suggestions'), )


class TransmitterManager(models.Manager):  # pylint: disable=R0903
    """Django Manager for Transmitter objects"""
    def get_queryset(self):
        """Returns query of TransmitterEntries

        :returns: the latest revision of a TransmitterEntry for each
        TransmitterEntry uuid associated with this Satellite that is
        both reviewed and approved
        """
        subquery = TransmitterEntry.objects.filter(
            reviewed=True, approved=True
        ).filter(uuid=OuterRef('uuid')).order_by('-created')
        return super(TransmitterManager, self).get_queryset().filter(
            reviewed=True, approved=True
        ).filter(created=Subquery(subquery.values('created')[:1]))


class Transmitter(TransmitterEntry):
    """Associates a generic Transmitter object with their TransmitterEntries
    that are managed by TransmitterManager
    """
    objects = TransmitterManager()

    def __str__(self):
        return self.description

    class Meta:
        proxy = True


class Telemetry(models.Model):
    """Model for satellite telemetry decoders."""
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

    def get_kaitai_fields(self):
        """Return an empty-value dict of fields for this kaitai.io struct
        Beware the overuse of "decoder" in satnogsdecoders and "decoder" the
        field above in this Telemetry model"""
        results = {}
        try:
            decoder_class = getattr(satnogsdecoders.decoder, self.decoder.capitalize())
            results = satnogsdecoders.decoder.get_fields(decoder_class, empty=True)
        except AttributeError:
            pass
        return results


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

    def display_frame(self):
        """Returns the contents of the saved frame file for this DemodData

        :returns: the contents of the saved frame file for this DemodData
        """
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


class ExportedFrameset(models.Model):
    """Model for exported frames."""
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    satellite = models.ForeignKey(Satellite, null=True, on_delete=models.SET_NULL)
    exported_file = models.FileField(upload_to=_name_exported_frames, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)


class Artifact(models.Model):
    """Model for observation artifacts."""

    artifact_file = models.FileField(upload_to='artifacts/', blank=True, null=True)

    network_obs_id = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return 'artifact-{0}'.format(self.id)


post_save.connect(_extract_network_obs_id, sender=Artifact)
