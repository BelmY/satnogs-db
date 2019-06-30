from __future__ import absolute_import, division, print_function, \
    unicode_literals

import logging
from datetime import datetime
from socket import error as socket_error

from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from db.base.models import DemodData, Mode, Satellite, Telemetry, \
    Transmitter, TransmitterEntry, TransmitterSuggestion
from db.base.tasks import check_celery, decode_all_data

logger = logging.getLogger('db')


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    list_display = ('name', 'norad_cat_id', 'status', 'decayed')
    search_fields = ('name', 'norad_cat_id')
    list_filter = ('status', 'decayed')

    def get_urls(self):
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

    def check_celery(self, request):
        try:
            investigator = check_celery.delay()
        except socket_error as e:
            messages.error(request, 'Cannot connect to broker: %s' % e)
            return HttpResponseRedirect(reverse('admin:index'))

        try:
            investigator.get(timeout=5)
        except investigator.TimeoutError as e:
            messages.error(request, 'Worker timeout: %s' % e)
        else:
            messages.success(request, 'Celery is OK')
        finally:
            return HttpResponseRedirect(reverse('admin:index'))

    # force a decode of all data for a norad ID. This could be very resource
    # intensive but necessary when catching a satellite up with a new decoder
    def decode_all_data(self, request, norad):
        decode_all_data.delay(norad)
        messages.success(request, 'Decode task was triggered successfully!')
        return redirect(reverse('admin:index'))


@admin.register(TransmitterEntry)
class TransmitterEntryAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'description', 'satellite', 'type', 'mode', 'baud', 'downlink_low',
        'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high', 'uplink_drift', 'reviewed',
        'approved', 'status', 'created', 'citation', 'user'
    )
    search_fields = ('satellite__id', 'uuid', 'satellite__name', 'satellite__norad_cat_id')
    list_filter = (
        'reviewed',
        'approved',
        'type',
        'status',
        'mode',
        'baud',
    )
    readonly_fields = ('uuid', 'satellite')


@admin.register(TransmitterSuggestion)
class TransmitterSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        'uuid', 'description', 'satellite', 'type', 'mode', 'baud', 'downlink_low',
        'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high', 'uplink_drift', 'status',
        'created', 'citation', 'user'
    )
    search_fields = ('satellite__id', 'uuid', 'satellite__name', 'satellite__norad_cat_id')
    list_filter = (
        'type',
        'mode',
        'baud',
    )
    readonly_fields = (
        'uuid', 'description', 'status', 'type', 'uplink_low', 'uplink_high', 'uplink_drift',
        'downlink_low', 'downlink_high', 'downlink_drift', 'mode', 'invert', 'baud', 'satellite',
        'reviewed', 'approved', 'created', 'citation', 'user'
    )
    actions = ['approve_suggestion', 'reject_suggestion']

    def get_actions(self, request):
        actions = super(TransmitterSuggestionAdmin, self).get_actions(request)
        if not request.user.has_perm('base.delete_transmittersuggestion'):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def approve_suggestion(self, request, queryset):
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
    list_display = (
        'uuid', 'description', 'satellite', 'type', 'mode', 'baud', 'downlink_low',
        'downlink_high', 'downlink_drift', 'uplink_low', 'uplink_high', 'uplink_drift', 'status',
        'created', 'citation', 'user'
    )
    search_fields = ('satellite__id', 'uuid', 'satellite__name', 'satellite__norad_cat_id')
    list_filter = (
        'type',
        'status',
        'mode',
        'baud',
    )
    readonly_fields = ('uuid', 'satellite')


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ('name', 'decoder')


@admin.register(DemodData)
class DemodDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'satellite', 'app_source', 'observer')
    search_fields = ('transmitter__uuid', 'satellite__norad_cat_id', 'observer')

    def satellite(self, obj):
        return obj.satellite
