"""SatNOGS DB API serializers, django rest framework"""
#  pylint: disable=R0201
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from rest_framework import serializers

from db.base.models import TRANSMITTER_STATUS, DemodData, Mode, Satellite, \
    Telemetry, Transmitter


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

    class Meta:
        model = Satellite
        fields = ('norad_cat_id', 'name', 'names', 'image', 'status', 'decayed', 'telemetries')


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
            'invert', 'baud', 'norad_cat_id', 'status', 'updated', 'citation', 'service'
        )

    # Keeping alive field for compatibility issues
    def get_alive(self, obj):
        """Returns transmitter status"""
        return obj.status == TRANSMITTER_STATUS[0]

    def get_mode_id(self, obj):
        """Returns downlink mode id"""
        return obj.downlink_mode.id

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
        fields = ('satellite', 'payload_frame', 'station', 'lat', 'lng', 'timestamp', 'app_source')
