"""SatNOGS DB API django rest framework Views"""
from django.core.files.base import ContentFile
from django.db.models import F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, \
    extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from db.api import filters, pagination, serializers
from db.api.perms import SafeMethodsWithPermission
from db.api.renderers import BrowserableJSONLDRenderer, JSONLDRenderer
from db.base.helpers import gridsquare
from db.base.models import SATELLITE_STATUS, SERVICE_TYPE, TRANSMITTER_STATUS, TRANSMITTER_TYPE, \
    Artifact, DemodData, LatestTleSet, Mode, Satellite, Transmitter
from db.base.tasks import decode_current_frame, publish_current_frame, update_satellite

ISS_EXAMPLE = OpenApiExample('25544 (ISS)', value=25544)


@extend_schema_view(
    retrieve=extend_schema(
        description='Retrieve a single RF Mode from SatNOGS DB based on its ID',
    ),
    list=extend_schema(description='Retrieve a complete list of RF Modes from SatNOGS DB', )
)
class ModeViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """
    Read-only view into the transmitter modulation modes (RF Modes) currently tracked
    in the SatNOGS DB database

    For more details on individual RF mode types please [see our wiki][moderef].

    [moderef]: https://wiki.satnogs.org/Category:RF_Modes
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    queryset = Mode.objects.all()
    serializer_class = serializers.ModeSerializer


@extend_schema_view(
    list=extend_schema(
        description='Retrieve a full or filtered list of satellites in SatNOGS DB',
        parameters=[
            # drf-spectacular does not currently recognize the in_orbit filter as a
            # bool, forcing it here. See drf-spectacular#234
            OpenApiParameter(
                name='in_orbit',
                description='Filter by satellites currently in orbit (True) or those that have \
                            decayed (False)',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='status',
                description='Filter by satellite status: ' + ' '.join(SATELLITE_STATUS),
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='norad_cat_id',
                description='Select a satellite by its NORAD-assigned identifier',
                examples=[ISS_EXAMPLE],
            ),
        ],
    ),
    retrieve=extend_schema(
        description='Retrieve details on a single satellite in SatNOGS DB',
        parameters=[
            OpenApiParameter(
                'norad_cat_id',
                OpenApiTypes.INT64,
                OpenApiParameter.PATH,
                description='Select a satellite by its NORAD-assigned identifier',
                examples=[ISS_EXAMPLE],
            ),
        ],
    ),
)
class SatelliteViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """
    Read-only view into the Satellite entities in the SatNOGS DB database
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    queryset = Satellite.objects.all()
    serializer_class = serializers.SatelliteSerializer
    filterset_class = filters.SatelliteViewFilter
    lookup_field = 'norad_cat_id'


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='satellite__norad_cat_id',
                description='NORAD ID of a satellite to filter telemetry data for',
                examples=[ISS_EXAMPLE],
            ),
            OpenApiParameter(
                name='status',
                description='Filter by transmitter status: ' + ' '.join(TRANSMITTER_STATUS),
                required=False,
                type=OpenApiTypes.STR,
                examples=[OpenApiExample('active', value='\'active\'')]
            ),
            OpenApiParameter(
                name='service',
                description='Filter by transmitter service: ' + ' '.join(SERVICE_TYPE),
                required=False,
                type=OpenApiTypes.STR,
                examples=[OpenApiExample('Amateur', value='\'Amateur\'')]
            ),
            OpenApiParameter(
                name='type',
                description='Filter by transmitter type: ' + ' '.join(TRANSMITTER_TYPE),
                required=False,
                type=OpenApiTypes.STR,
                examples=[OpenApiExample('Transmitter', value='\'Transmitter\'')]
            ),
        ],
    ),
)
class TransmitterViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """
    Read-only view into the Transmitter entities in the SatNOGS DB database.
    Transmitters are inclusive of Transceivers and Transponders
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    queryset = Transmitter.objects.all()
    serializer_class = serializers.TransmitterSerializer
    filterset_class = filters.TransmitterViewFilter
    lookup_field = 'uuid'


class LatestTleSetViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=R0901
    """
    Read-only view into the most recent two-line elements (TLE) in the SatNOGS DB
    database
    """
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    queryset = LatestTleSet.objects.all().select_related('satellite').exclude(
        latest_distributable__isnull=True
    ).annotate(
        tle0=F('latest_distributable__tle0'),
        tle1=F('latest_distributable__tle1'),
        tle2=F('latest_distributable__tle2'),
        tle_source=F('latest_distributable__tle_source'),
        updated=F('latest_distributable__updated')
    )
    serializer_class = serializers.LatestTleSetSerializer
    filterset_class = filters.LatestTleSetViewFilter

    def get_queryset(self):
        """
        Returns latest TLE queryset depending on user permissions
        """
        if self.request.user.has_perm('base.access_all_tles'):
            return LatestTleSet.objects.all().select_related('satellite').exclude(
                latest__isnull=True
            ).annotate(
                tle0=F('latest__tle0'),
                tle1=F('latest__tle1'),
                tle2=F('latest__tle2'),
                tle_source=F('latest__tle_source'),
                updated=F('latest__updated')
            )
        return self.queryset


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='app_source',
                description='The submission source for the telemetry frames: manual (a manual \
                             upload/entry), network (SatNOGS Network observations), or sids \
                             (legacy API submission)',
            ),
            OpenApiParameter(
                name='observer',
                description='(string) name of the observer (submitter) to retrieve telemetry data \
                            from'
            ),
            OpenApiParameter(
                name='satellite',
                description='NORAD ID of a satellite to filter telemetry data for',
                examples=[ISS_EXAMPLE],
            ),
            OpenApiParameter(name='transmitter', description='Not currently in use'),
        ],
    ),
)
class TelemetryViewSet(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    """
    View into the Telemetry objects in the SatNOGS DB database. Currently,
    this table is inclusive of all data collected from satellite downlink
    observations
    """
    renderer_classes = [
        JSONRenderer, BrowsableAPIRenderer, JSONLDRenderer, BrowserableJSONLDRenderer
    ]
    queryset = DemodData.objects.all()
    serializer_class = serializers.TelemetrySerializer
    filterset_class = filters.TelemetryViewFilter
    permission_classes = [SafeMethodsWithPermission]
    parser_classes = (FormParser, FileUploadParser)
    pagination_class = pagination.LinkedHeaderPageNumberPagination

    @extend_schema(
        responses={'201': None},  # None
    )
    def create(self, request, *args, **kwargs):
        """
        Creates an frame of telemetry data from a satellite observation.
        """
        data = {}

        norad_cat_id = request.data.get('noradID')

        if not Satellite.objects.filter(norad_cat_id=norad_cat_id).exists():
            try:
                update_satellite(norad_cat_id, update_name=True)
            except LookupError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        data['satellite'] = Satellite.objects.get(norad_cat_id=norad_cat_id).id
        data['station'] = request.data.get('source')
        timestamp = request.data.get('timestamp')
        data['timestamp'] = timestamp
        if request.data.get('version'):
            data['version'] = request.data.get('version')

        # Convert coordinates to omit N-S and W-E designators
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        if any(x.isalpha() for x in lat):
            data['lat'] = (-float(lat[:-1]) if ('S' in lat) else float(lat[:-1]))
        else:
            data['lat'] = float(lat)
        if any(x.isalpha() for x in lng):
            data['lng'] = (-float(lng[:-1]) if ('W' in lng) else float(lng[:-1]))
        else:
            data['lng'] = float(lng)

        # Network or SiDS submission?
        if request.data.get('satnogs_network'):
            data['app_source'] = 'network'
        else:
            data['app_source'] = 'sids'

        # Create file out of frame string
        frame = ContentFile(request.data.get('frame'), name='sids')
        data['payload_frame'] = frame
        # Create observer
        qth = gridsquare(data['lat'], data['lng'])
        observer = '{0}-{1}'.format(data['station'], qth)
        data['observer'] = observer

        serializer = serializers.SidsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Run task to decode the current frame
        decode_current_frame.delay(norad_cat_id, serializer.instance.pk)

        # Run task to publish the current frame via ZeroMQ
        publish_current_frame.delay(norad_cat_id, timestamp, request.data.get('frame'), observer)

        return Response(status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'network_obs_id',
                OpenApiTypes.INT64,
                required=False,
                description='Given a SatNOGS Network observation ID, this will return any \
                             artifacts files associated with the observation.'
            ),
        ],
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                'id',
                OpenApiTypes.URI,
                OpenApiParameter.PATH,
                description='The ID for the requested artifact entry in DB'
            ),
        ],
    ),
)
class ArtifactViewSet(  # pylint: disable=R0901
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
        viewsets.GenericViewSet):
    """
    Artifacts are file-formatted objects collected from a satellite observation.
    """
    queryset = Artifact.objects.all()
    filterset_class = filters.ArtifactViewFilter
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser, MultiPartParser)
    pagination_class = pagination.LinkedHeaderPageNumberPagination

    def get_serializer_class(self):
        """Returns the right serializer depending on http method that is used"""
        if self.action == 'create':
            return serializers.NewArtifactSerializer
        return serializers.ArtifactSerializer

    def create(self, request, *args, **kwargs):
        """
        Creates observation artifact from an [HDF5 formatted file][hdf5ref]
        * Requires session or key authentication to create an artifact

        [hdf5ref]: https://en.wikipedia.org/wiki/Hierarchical_Data_Format
        """
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                data = serializer.save()
                http_response = {}
                http_response['id'] = data.id
                response = Response(http_response, status=status.HTTP_200_OK)
            else:
                data = serializer.errors
                response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        except (ValidationError, ValueError, OSError) as error:
            response = Response(str(error), status=status.HTTP_400_BAD_REQUEST)
        return response
