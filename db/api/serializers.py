"""SatNOGS DB API serializers, django rest framework"""
#  pylint: disable=R0201

import h5py
from rest_framework import serializers

from db.base.models import TRANSMITTER_STATUS, Artifact, DemodData, LatestTleSet, Mode, \
    Satellite, Telemetry, Transmitter


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

    def get_operator(self, obj):
        """Returns operator text"""
        return str(obj.operator)

    def get_countries(self, obj):
        """Returns countires"""
        return ','.join(map(str, obj.countries))


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
    def get_alive(self, obj):
        """Returns transmitter status"""
        return obj.status == TRANSMITTER_STATUS[0]

    def get_mode_id(self, obj):
        """Returns downlink mode id"""
        try:
            return obj.downlink_mode.id
        except AttributeError:  # rare chance that this happens in prod
            return None

    def get_mode(self, obj):
        """Returns downlink mode name"""
        try:
            return obj.downlink_mode.name
        except Exception:  # pylint: disable=W0703
            return None

    def get_uplink_mode(self, obj):
        """Returns uplink mode name"""
        try:
            return obj.uplink_mode.name
        except Exception:  # pylint: disable=W0703
            return None

    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        return obj.satellite.norad_cat_id


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

    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID"""
        return obj.satellite.norad_cat_id

    def get_tle0(self, obj):
        """Returns TLE line 0"""
        return obj.tle0

    def get_tle1(self, obj):
        """Returns TLE line 1"""
        return obj.tle1

    def get_tle2(self, obj):
        """Returns TLE line 2"""
        return obj.tle2

    def get_tle_source(self, obj):
        """Returns TLE source"""
        return obj.tle_source

    def get_updated(self, obj):
        """Returns TLE updated datetime"""
        return obj.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


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

    def get_norad_cat_id(self, obj):
        """Returns Satellite NORAD ID for this Transmitter"""
        return obj.satellite.norad_cat_id

    def get_transmitter(self, obj):
        """Returns Transmitter UUID"""
        try:
            return obj.transmitter.uuid
        except Exception:  # pylint: disable=W0703
            return ''

    def get_schema(self, obj):
        """Returns Transmitter telemetry schema"""
        try:
            return obj.payload_telemetry.schema
        except Exception:  # pylint: disable=W0703
            return ''

    def get_decoded(self, obj):
        """Returns the payload_decoded field"""
        return obj.payload_decoded

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


class ArtifactSerializer(serializers.ModelSerializer):
    """SatNOGS DB Artifacts API Serializer"""
    class Meta:
        model = Artifact
        fields = ('id', 'network_obs_id', 'artifact_file')


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
        except OSError as error:
            raise serializers.ValidationError(
                'Not a valid HDF5 file: {}'.format(error), code='invalid'
            )

        return attrs

    class Meta:
        model = Artifact
        fields = ('artifact_file', )
