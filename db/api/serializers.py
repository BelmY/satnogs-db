from db.base.models import TRANSMITTER_STATUS, DemodData, Mode, Satellite, \
    Transmitter
from rest_framework import serializers


class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
        fields = ('id', 'name')


class SatelliteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Satellite
        fields = ('norad_cat_id', 'name', 'names', 'image', 'status', 'decayed')


class TransmitterSerializer(serializers.ModelSerializer):
    norad_cat_id = serializers.SerializerMethodField()
    mode_id = serializers.SerializerMethodField()
    mode = serializers.SerializerMethodField()
    alive = serializers.SerializerMethodField()
    updated = serializers.DateTimeField(source='created')

    class Meta:
        model = Transmitter
        fields = (
            'uuid', 'description', 'alive', 'type', 'uplink_low', 'uplink_high', 'uplink_drift',
            'downlink_low', 'downlink_high', 'downlink_drift', 'mode_id', 'mode', 'invert', 'baud',
            'norad_cat_id', 'status', 'updated', 'citation'
        )

    # Keeping alive field for compatibility issues
    def get_alive(self, obj):
        return obj.status == TRANSMITTER_STATUS[0]

    def get_mode_id(self, obj):
        try:
            return obj.mode.id
        except Exception:
            return None

    def get_mode(self, obj):
        try:
            return obj.mode.name
        except Exception:
            return None

    def get_norad_cat_id(self, obj):
        return obj.satellite.norad_cat_id


class TelemetrySerializer(serializers.ModelSerializer):
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
        return obj.satellite.norad_cat_id

    def get_transmitter(self, obj):
        try:
            return obj.transmitter.uuid
        except Exception:
            return ''

    def get_schema(self, obj):
        try:
            return obj.payload_telemetry.schema
        except Exception:
            return ''

    def get_decoded(self, obj):
        return obj.payload_decoded

    def get_frame(self, obj):
        return obj.display_frame()


class SidsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemodData
        fields = ('satellite', 'payload_frame', 'station', 'lat', 'lng', 'timestamp', 'app_source')
