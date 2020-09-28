"""Defines functions and settings for the django admin interface"""
from datetime import datetime
from socket import error as socket_error

from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from db.base.models import Artifact, DemodData, ExportedFrameset, LatestTleSet, Mode, Operator, \
    Satellite, Telemetry, Tle, Transmitter, TransmitterEntry, TransmitterSuggestion
from db.base.tasks import check_celery, decode_all_data, update_tle_sets
from db.base.utils import update_latest_tle_sets


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    """Defines Mode view in django admin UI"""
    list_display = ('name', )


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    """Defines Operator view in django admin UI"""
    list_display = ('name', 'names', 'website')
    search_fields = ('name', 'names')


@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    """Defines Satellite view in django admin UI"""
    list_display = ('id', 'name', 'norad_cat_id', 'status', 'decayed', 'norad_follow_id')
    search_fields = ('name', 'norad_cat_id', 'norad_follow_id')
    list_filter = ('status', 'decayed')

    def get_urls(self):
        """Returns django urls for the Satellite view

        check_celery -- url for the check_celery function
        decode_all_data -- url for the decode_all_data function

        :returns: Django urls for the Satellite admin view
        """
        urls = super(SatelliteAdmin, self).get_urls()
        my_urls = [
            url(r'^check_celery/$', self.check_celery, name='check_celery'),
            url(
                r'^decode_all_data/(?P<norad>[0-9]+)/$',
                self.decode_all_data,
                name='decode_all_data'
            ),
        ]
        return my_urls + urls

    def check_celery(self, request):  # pylint: disable=R0201
        """Returns status of Celery workers

        Check the delay for celery workers, return an error if a connection
        can not be made or if the delay is too long. Otherwise return that
        Celery is OK.

        :returns: admin home page redirect with popup message
        """
        try:
            investigator = check_celery.delay()
        except socket_error as error:
            messages.error(request, 'Cannot connect to broker: %s' % error)
            return HttpResponseRedirect(reverse('admin:index'))

        try:
            investigator.get(timeout=5)
        except investigator.TimeoutError as error:
            messages.error(request, 'Worker timeout: %s' % error)
        else:
            messages.success(request, 'Celery is OK')

        return HttpResponseRedirect(reverse('admin:index'))

    def decode_all_data(self, request, norad):  # pylint: disable=R0201
        """Returns the admin home page, while triggering a Celery decode task

        Forces a decode of all data for a norad ID. This could be very resource
        intensive but necessary when catching a satellite up with a new decoder

        :param norad: the NORAD ID for the satellite to decode
        :returns: Admin home page
        """
        decode_all_data.delay(norad)
        messages.success(request, 'Decode task was triggered successfully!')
        return redirect(reverse('admin:index'))


@admin.register(TransmitterEntry)
class TransmitterEntryAdmin(admin.ModelAdmin):
    """Defines TransmitterEntry view in django admin UI"""
    list_display = (
        'uuid', 'description', 'satellite', 'service', 'type', 'downlink_mode', 'uplink_mode',
        'baud', 'downlink_low', 'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high',
        'uplink_drift', 'reviewed', 'approved', 'status', 'created', 'citation', 'user'
    )
    search_fields = ('satellite__id', 'uuid', 'satellite__name', 'satellite__norad_cat_id')
    list_filter = (
        'reviewed',
        'approved',
        'type',
        'status',
        'service',
        'downlink_mode',
        'uplink_mode',
        'baud',
    )
    readonly_fields = ('uuid', 'satellite')


@admin.register(TransmitterSuggestion)
class TransmitterSuggestionAdmin(admin.ModelAdmin):
    """Defines TransmitterSuggestion view in django admin UI"""
    list_display = (
        'uuid', 'description', 'satellite', 'service', 'type', 'downlink_mode', 'uplink_mode',
        'baud', 'downlink_low', 'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high',
        'uplink_drift', 'status', 'created', 'citation', 'user'
    )
    search_fields = ('satellite__id', 'uuid', 'satellite__name', 'satellite__norad_cat_id')
    list_filter = (
        'type',
        'downlink_mode',
        'uplink_mode',
        'baud',
        'service',
    )
    readonly_fields = (
        'uuid', 'description', 'status', 'type', 'uplink_low', 'uplink_high', 'uplink_drift',
        'downlink_low', 'downlink_high', 'downlink_drift', 'downlink_mode', 'uplink_mode',
        'invert', 'baud', 'satellite', 'reviewed', 'approved', 'created', 'citation', 'user',
        'service'
    )
    actions = ['approve_suggestion', 'reject_suggestion']

    def get_actions(self, request):
        """Returns the actions a user can take on a TransmitterSuggestion

        For example, delete, approve, or reject

        :returns: list of actions the user can take on TransmitterSuggestion
        """
        actions = super(TransmitterSuggestionAdmin, self).get_actions(request)
        if not request.user.has_perm('base.delete_transmittersuggestion'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def approve_suggestion(self, request, queryset):
        """Returns the TransmitterSuggestion page after approving suggestions

        :param queryset: the TransmitterSuggestion entries to be approved
        :returns: TransmitterSuggestion admin page
        """
        queryset_size = len(queryset)
        for entry in queryset:
            entry.approved = True
            entry.reviewed = True
            entry.created = datetime.utcnow()
            entry.user = request.user
            entry.save()
        # After creating the new approved entries, we update the suggestion entries as reviewed
        # Note that queryset.update doesn't use model's save() that creates new entries
        queryset.update(reviewed=True, approved=True)
        if queryset_size == 1:
            self.message_user(request, "Transmitter suggestion was successfully approved")
        else:
            self.message_user(request, "Transmitter suggestions were successfully approved")

    approve_suggestion.short_description = 'Approve selected transmitter suggestions'

    def reject_suggestion(self, request, queryset):
        """Returns the TransmitterSuggestion page after rejecting suggestions

        :param queryset: the TransmitterSuggestion entries to be rejected
        :returns: TransmitterSuggestion admin page
        """
        queryset_size = len(queryset)
        for entry in queryset:
            entry.created = datetime.utcnow()
            entry.user = request.user
            entry.approved = False
            entry.reviewed = True
            entry.save()
        # After creating the new approved entries, we update the suggestion entries as reviewed
        # Note that queryset.update doesn't use model's save() that creates new entries
        queryset.update(reviewed=True, approved=False)
        if queryset_size == 1:
            self.message_user(request, "Transmitter suggestion was successfully rejected")
        else:
            self.message_user(request, "Transmitter suggestions were successfully rejected")

    reject_suggestion.short_description = 'Reject selected transmitter suggestions'


@admin.register(Transmitter)
class TransmitterAdmin(admin.ModelAdmin):
    """Defines Transmitter view in django admin UI"""
    list_display = (
        'uuid', 'description', 'satellite', 'service', 'type', 'downlink_mode', 'uplink_mode',
        'baud', 'downlink_low', 'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high',
        'uplink_drift', 'status', 'created', 'citation', 'user'
    )
    search_fields = (
        'satellite__id', 'uuid', 'description', 'satellite__name', 'satellite__norad_cat_id'
    )
    list_filter = (
        'type',
        'status',
        'service',
        'downlink_mode',
        'uplink_mode',
        'baud',
    )
    readonly_fields = ('uuid', 'satellite')


@admin.register(Tle)
class TleAdmin(admin.ModelAdmin):
    """Define TLE view in django admin UI"""
    list_display = ('satellite_name', 'tle0', 'tle1', 'updated', 'tle_source')
    list_filter = ('tle_source', 'satellite__name')

    def satellite_name(self, obj):  # pylint: disable=no-self-use
        """Return the satellite name"""
        return obj.satellite.name

    def get_urls(self):
        """Returns django urls for Tle view

        update_tle_sets -- url for the update_tle_sets function

        :returns: Django urls for the Tle admin view
        """
        urls = super(TleAdmin, self).get_urls()
        my_urls = [
            url(r'^update_tle_sets/$', self.update_tle_sets, name='update_tle_sets'),
        ]
        return my_urls + urls

    def update_tle_sets(self, request):  # pylint: disable=R0201
        """Returns the admin home page, while triggering a Celery update tle sets task

        :returns: Admin home page
        """
        update_tle_sets.delay()
        messages.success(request, 'Update TLE sets task was triggered successfully!')
        return redirect(reverse('admin:index'))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        update_latest_tle_sets(satellite_ids=[obj.satellite.pk])

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        update_latest_tle_sets(satellite_ids=[obj.satellite.pk])

    def delete_queryset(self, request, queryset):
        satellites = [tle.satellite.pk for tle in queryset]
        super().delete_queryset(request, queryset)
        update_latest_tle_sets(satellite_ids=satellites)


@admin.register(LatestTleSet)
class LatestTleSetAdmin(admin.ModelAdmin):
    """Defines LatestTleSet view in django admin UI"""
    list_display = ('satellite', 'latest', 'latest_distributable', 'last_modified')
    list_filter = ('satellite__name', )


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    """Defines Telemetry view in django admin UI"""
    list_display = ('name', 'decoder')


@admin.register(DemodData)
class DemodDataAdmin(admin.ModelAdmin):
    """Defines DemodData view in django admin UI"""
    list_display = ('id', 'satellite', 'app_source', 'observer')
    search_fields = ('transmitter__uuid', 'satellite__norad_cat_id', 'observer')
    list_filter = (
        'satellite',
        'app_source',
        'observer',
    )

    def satellite(self, obj):  # pylint: disable=R0201
        """Returns the Satellite object associated with this DemodData

        :param obj: DemodData object
        :returns: Satellite object
        """
        return obj.satellite


@admin.register(ExportedFrameset)
class ExportedFramesetAdmin(admin.ModelAdmin):
    """Defines ExportedFrameset view in django admin UI"""
    list_display = ('id', 'created', 'user', 'satellite', 'exported_file', 'start', 'end')
    search_fields = ('user', 'satellite__norad_cat_id')
    list_filter = ('satellite', 'user')


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    """Defines Artifact view in django admin UI"""
    list_display = ('id', 'network_obs_id', 'artifact_file')
