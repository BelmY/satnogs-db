import django_filters
from db.base.models import DemodData, Satellite, Transmitter
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet


class TransmitterViewFilter(FilterSet):
    alive = filters.BooleanFilter(field_name='status', label='Alive', method='filter_status')

    def filter_status(self, queryset, name, value):
        if value:
            return queryset.filter(status='functional')
        else:
            return queryset.exclude(status='functional')

    class Meta:
        model = Transmitter
        fields = ['uuid', 'mode', 'type', 'satellite__norad_cat_id', 'alive', 'status']


class SatelliteViewFilter(FilterSet):
    ''' filter on decayed field '''
    in_orbit = filters.BooleanFilter(field_name='decayed', label='In orbit', lookup_expr='isnull')

    class Meta:
        model = Satellite
        fields = ['norad_cat_id', 'status']


class TelemetryViewFilter(FilterSet):
    satellite = django_filters.NumberFilter(
        field_name='satellite__norad_cat_id', lookup_expr='exact'
    )

    class Meta:
        model = DemodData
        fields = ['satellite']
