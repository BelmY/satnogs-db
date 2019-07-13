"""SatNOGS DB django rest framework Filters class"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import django_filters
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet

from db.base.models import DemodData, Satellite, Transmitter


class TransmitterViewFilter(FilterSet):
    """SatNOGS DB Transmitter API View Filter"""
    alive = filters.BooleanFilter(field_name='status', label='Alive', method='filter_status')

    #  see https://django-filter.readthedocs.io/en/master/ref/filters.html for
    #  unused-argument
    def filter_status(self, queryset, name, value):  # pylint: disable=unused-argument,no-self-use
        """Returns Transmitters that are either functional or non-functional"""
        if value:
            return queryset.filter(status='active')
        else:
            return queryset.exclude(status='active')

    class Meta:
        model = Transmitter
        fields = ['uuid', 'mode', 'type', 'satellite__norad_cat_id', 'alive', 'status', 'service']


class SatelliteViewFilter(FilterSet):
    """SatNOGS DB Satellite API View Filter

    filter on decayed field
    """
    in_orbit = filters.BooleanFilter(field_name='decayed', label='In orbit', lookup_expr='isnull')

    class Meta:
        model = Satellite
        fields = ['norad_cat_id', 'status']


class TelemetryViewFilter(FilterSet):
    """SatNOGS DB Telemetry API View Filter"""
    satellite = django_filters.NumberFilter(
        field_name='satellite__norad_cat_id', lookup_expr='exact'
    )

    class Meta:
        model = DemodData
        fields = ['satellite']
