"""SatNOGS DB API serializers, django rest framework"""
#  pylint: disable=R0201

import h5py
from django.utils.datastructures import MultiValueDictKeyError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema_field, extend_schema_serializer
from rest_framework import serializers

from db.base.models import TRANSMITTER_STATUS, Artifact, DemodData, LatestTleSet, Mode, \
    Satellite, Telemetry, Transmitter


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Mode Example 1',
            summary='Example: list all modes',
            description='This is a truncated example response for listing all RF Mode entries',
            value=[
                {
                    'id': 49,
                    'name': 'AFSK'
                },
            ],
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class ModeSerializer(serializers.ModelSerializer):
    """SatNOGS DB Mode API Serializer"""
    class Meta:
        model = Mode
        fields = ('id', 'name')


class SatTelemetrySerializer(serializers.ModelSerializer):
    """SatNOGS DB satellite telemetry API Serializer"""
    class Meta:
        model = Telemetry
        fields = ['decoder']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Satellite Example 1',
            summary='Example: retrieving ISS',
            description='This is an example response for retrieving the ISS entry, NORAD ID 25544',
            value={
                'norad_cat_id': 25544,
                'name': 'ISS',
                'names': 'ZARYA',
                'image': 'https://db-satnogs.freetls.fastly.net/media/satellites/ISS.jpg',
                'status': 'alive',
                'decayed': None,
                'launched': '1998-11-20T00:00:00Z',
                'deployed': '1998-11-20T00:00:00Z',
                'website': 'https://www.nasa.gov/mission_pages/station/main/index.html',
                'operator': 'None',
                'countries': 'RU,US',
                'telemetries': [{
                    'decoder': 'iss'
                }]
            },
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class SatelliteSerializer(serializers.ModelSerializer):
    """SatNOGS DB Satellite API Serializer"""

    telemetries = SatTelemetrySerializer(many=True, read_only=True)
    countries = serializers.SerializerMethodField()
    operator = serializers.SerializerMethodField()

    class Meta:
        model = Satellite
        fields = (
            'norad_cat_id', 'name', 'names', 'image', 'status', 'decayed', 'launched', 'deployed',
            'website', 'operator', 'countries', 'telemetries'
        )

    @extend_schema_field(OpenApiTypes.STR)
    def get_operator(self, obj):
        """Returns operator text"""
        return str(obj.operator)

    @extend_schema_field(OpenApiTypes.STR)
    def get_countries(self, obj):
        """Returns countires"""
        return ','.join(map(str, obj.countries))


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Transmitter Example 1',
            summary='Example: Transmitter API response',
            value={
                'uuid': 'eozSf5mKyzNxoascs8V4bV',
                'description': 'Mode V/U FM - Voice Repeater',
                'alive': True,
                'type': 'Transceiver',
                'uplink_low': 145990000,
                'uplink_high': None,
                'uplink_drift': None,
                'downlink_low': 437800000,
                'downlink_high': None,
                'downlink_drift': None,
                'mode': 'FM',
                'mode_id': 1,
                'uplink_mode': 'FM',
                'invert': False,
                'baud': None,
                'norad_cat_id': 25544,
                'status': 'active',
                'updated': '2020-09-03T13:14:41.552071Z',
                'citation': 'https://www.ariss.org/press-releases/september-2-2020',
                'service': 'Amateur',
                'coordination': '',
                'coordination_url': ''
            },
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class TransmitterSerializer(serializers.ModelSerializer):
    """SatNOGS DB Transmitter API Serializer"""
    norad_cat_id = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    mode_id = serializers.SerializerMethodField()
    uplink_mode = serializers.SerializerMethodField()
    alive = serializers.SerializerMethodField()
    updated = serializers.DateTimeField(source='created')

    class Meta:
        model = Transmitter
        fields = (
            'uuid', 'description', 'alive', 'type', 'uplink_low', 'uplink_high', 'uplink_drift',
            'downlink_low', 'downlink_high', 'downlink_drift', 'mode', 'mode_id', 'uplink_mode',
            'invert', 'baud', 'norad_cat_id', 'status', 'updated', 'citation', 'service',
            'coordination', 'coordination_url'
        )

    # Keeping alive field for compatibility issues
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_alive(self, obj):
        """Returns transmitter status"""
        return obj.status == TRANSMITTER_STATUS[0]

    @extend_schema_field(OpenApiTypes.INT)
    def get_mode_id(self, obj):
        """Returns downlink mode id"""
        try:
            return obj.downlink_mode.id
        except AttributeError:  # rare chance that this happens in prod
            return None

    @extend_schema_field(OpenApiTypes.INT)
    def get_mode(self, obj):
        """Returns downlink mode name"""
        try:
            return obj.downlink_mode.name
        except AttributeError:
            return None

    @extend_schema_field(OpenApiTypes.INT)
    def get_uplink_mode(self, obj):
        """Returns uplink mode name"""
        try:
            return obj.uplink_mode.name
        except AttributeError:
            return None

    @extend_schema_field(OpenApiTypes.INT64)
    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        try:
            return obj.satellite.norad_cat_id
        except AttributeError:
            return None


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'TLE Example 1',
            summary='Example: TLE API response',
            value={
                'tle0': '0 ISS (ZARYA)',
                'tle1': '1 25544U 98067A   21009.90234038  .00001675  00000-0  38183-4 0  9997',
                'tle2': '2 25544  51.6464  45.6388 0000512 205.3232 213.2158 15.49275327264062',
                'tle_source': 'undisclosed',
                'norad_cat_id': 25544,
                'updated': '2021-01-09T22:46:37.781923+0000'
            },
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class LatestTleSetSerializer(serializers.ModelSerializer):
    """SatNOGS DB LatestTleSet API Serializer"""

    norad_cat_id = serializers.SerializerMethodField()
    tle0 = serializers.SerializerMethodField()
    tle1 = serializers.SerializerMethodField()
    tle2 = serializers.SerializerMethodField()
    tle_source = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()

    class Meta:
        model = LatestTleSet
        fields = ('tle0', 'tle1', 'tle2', 'tle_source', 'norad_cat_id', 'updated')

    @extend_schema_field(OpenApiTypes.INT64)
    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        return obj.satellite.norad_cat_id

    @extend_schema_field(OpenApiTypes.STR)
    def get_tle0(self, obj):
        """Returns TLE line 0"""
        return obj.tle0

    @extend_schema_field(OpenApiTypes.STR)
    def get_tle1(self, obj):
        """Returns TLE line 1"""
        return obj.tle1

    @extend_schema_field(OpenApiTypes.STR)
    def get_tle2(self, obj):
        """Returns TLE line 2"""
        return obj.tle2

    @extend_schema_field(OpenApiTypes.STR)
    def get_tle_source(self, obj):
        """Returns TLE source"""
        return obj.tle_source

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_updated(self, obj):
        """Returns TLE updated datetime"""
        return obj.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


@extend_schema_serializer(
    exclude_fields=('app_source', 'observer', 'timestamp'),
    examples=[
        OpenApiExample(
            'Telemetry Example 1',
            summary='Example: retrieving a single Telemetry frame',
            description='This is an example response for retrieving a single data frame',
            value={
                'norad_cat_id': 40379,
                'transmitter': None,
                'app_source': 'network',
                'schema': None,
                'decoded': 'influxdb',
                'frame':
                '968870A6A0A66086A240404040E103F0ABCD0000004203F500B475E215EA5FA0040C000B00090001\
                0025008E55EE7B64650100000000AE4D07005D660F007673340000C522370067076507FD0C6000270\
                0FE0CC50E0D00AD0E0B069007BD0E0E00650D21001400FE0C910054007007690D8700FC0CBA00E407\
                43001C0F140077077807D7078E00120F240068076D07DA0A74003D0F2500830780077A0AC401490F9\
                60070077207FDFC9F079507950700C03B0015009AFF6900C8FFE0FFA700EBFF3A00F200F3FF02016D\
                0A590A0D0AE3099B0C830CB50DA70D9D06CC0043009401B8338B334C20001000000000009F0200000\
                3000000FF723D00BEFFFFFFFF2E89B0151C00',
                'observer': 'KB9JHU-EM69uf',
                'timestamp': '2021-01-05T22:28:09Z'
            },
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class TelemetrySerializer(serializers.ModelSerializer):
    """SatNOGS DB Telemetry API Serializer"""
    norad_cat_id = serializers.SerializerMethodField()
    transmitter = serializers.SerializerMethodField()
    schema = serializers.SerializerMethodField()
    decoded = serializers.SerializerMethodField()
    frame = serializers.SerializerMethodField()

    class Meta:
        model = DemodData
        fields = (
            'norad_cat_id', 'transmitter', 'app_source', 'schema', 'decoded', 'frame', 'observer',
            'timestamp'
        )

    @extend_schema_field(OpenApiTypes.INT64)
    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID for this Transmitter"""
        return obj.satellite.norad_cat_id

    @extend_schema_field(OpenApiTypes.UUID)
    def get_transmitter(self, obj):
        """Returns Transmitter UUID"""
        try:
            return obj.transmitter.uuid
        except AttributeError:
            return ''

    # deprecated, needs pulled out - cshields
    @extend_schema_field(OpenApiTypes.STR)
    def get_schema(self, obj):
        """Returns Transmitter telemetry schema"""
        try:
            return obj.payload_telemetry.schema
        except AttributeError:
            return ''

    @extend_schema_field(OpenApiTypes.STR)
    def get_decoded(self, obj):
        """Returns the payload_decoded field"""
        return obj.payload_decoded

    @extend_schema_field(OpenApiTypes.STR)
    def get_frame(self, obj):
        """Returns the payload frame"""
        return obj.display_frame()


class SidsSerializer(serializers.ModelSerializer):
    """SatNOGS DB SiDS API Serializer"""
    class Meta:
        model = DemodData
        fields = (
            'satellite', 'payload_frame', 'station', 'lat', 'lng', 'timestamp', 'app_source',
            'observer'
        )


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'View Artifact Example 1',
            summary='Example: retrieving a specific artifact',
            description='This is an example response when requesting a specific artifact \
                        previously uploaded to DB',
            value={
                'id':
                1337,
                'network_obs_id':
                3376466,
                'artifact_file':
                'http://db-dev.satnogs.org/media/artifacts/bba35b2d-76cc-4a8f-9b8a-4a2ecb09c6df.h5'
            },
            status_codes=['200'],
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class ArtifactSerializer(serializers.ModelSerializer):
    """SatNOGS DB Artifacts API Serializer"""
    class Meta:
        model = Artifact
        fields = ('id', 'network_obs_id', 'artifact_file')


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'New Artifact Example 1',
            summary='Example: uploading artifact',
            description='This is an example response after successfully uploading an artifact \
                        file. The ID of the artifact is returned',
            value={
                'id': 1337,
            },
            status_codes=['200', '201'],
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class NewArtifactSerializer(serializers.ModelSerializer):
    """SatNOGS Network New Artifact API Serializer"""
    def validate(self, attrs):
        """Validates data of incoming artifact"""

        try:
            with h5py.File(self.initial_data['artifact_file'], 'r') as h5_file:
                if 'artifact_version' not in h5_file.attrs:
                    raise serializers.ValidationError(
                        'Not a valid SatNOGS Artifact.', code='invalid'
                    )
        except (OSError, MultiValueDictKeyError) as error:
            raise serializers.ValidationError(
                'Not a valid HDF5 file: {}'.format(error), code='invalid'
            )

        return attrs

    class Meta:
        model = Artifact
        fields = ('artifact_file', )
