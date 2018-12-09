import logging
from socket import error as socket_error

from django.conf.urls import url
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from db.base.models import Mode, Satellite, Transmitter, Suggestion, DemodData, Telemetry
from db.base.tasks import check_celery, reset_decoded_data, decode_all_data


logger = logging.getLogger('db')


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    list_display = ('name', 'norad_cat_id')

    def get_urls(self):
        urls = super(SatelliteAdmin, self).get_urls()
        my_urls = [
            url(r'^check_celery/$', self.check_celery, name='check_celery'),
            url(r'^reset_data/(?P<norad>[0-9]+)/$', self.reset_data,
                name='reset_data'),
            url(r'^decode_all_data/(?P<norad>[0-9]+)/$', self.decode_all_data,
                name='decode_all_data'),
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

    # resets all decoded data and changes the is_decoded flag back to False
    # THIS IS VERY DISTRUCTIVE, but the expectation is that a decode_all_data
    # would follow.
    def reset_data(self, request, norad):
        reset_decoded_data.delay(norad)
        messages.success(request, 'Data reset task was triggered successfully!')
        return redirect(reverse('admin:index'))

    # force a decode of all data for a norad ID. This could be very resource
    # intensive but necessary when catching a satellite up with a new decoder
    def decode_all_data(self, request, norad):
        decode_all_data.delay(norad)
        messages.success(request, 'Decode task was triggered successfully!')
        return redirect(reverse('admin:index'))


@admin.register(Transmitter)
class TransmitterAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'description', 'satellite', 'type', 'alive', 'mode', 'uplink_low',
                    'uplink_high', 'uplink_drift', 'downlink_low', 'downlink_high',
                    'downlink_drift', 'baud',)
    search_fields = ('satellite__id', 'uuid', 'satellite__name', 'satellite__norad_cat_id')
    list_filter = ('type', 'alive', 'mode', 'baud',)
    readonly_fields = ('uuid', 'satellite', 'approved',)


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'description', 'transmitter_uuid', 'user', 'type', 'satellite',
                    'uplink_low', 'uplink_high', 'uplink_drift', 'downlink_low', 'downlink_high',
                    'downlink_drift',)
    search_fields = ('satellite', 'uuid',)
    list_filter = ('type', 'mode',)
    readonly_fields = ('uuid', 'satellite', 'transmitter', 'approved', 'user',
                       'citation', 'transmitter_data')
    actions = ['approve_suggestion']

    def approve_suggestion(self, request, queryset):
        for obj in queryset:
            try:
                transmitter = Transmitter.objects.get(id=obj.transmitter.id)
                transmitter.update_from_suggestion(obj)
                obj.delete()
            except (Transmitter.DoesNotExist, AttributeError):
                obj.approved = True
                obj.citation = ''
                obj.user = None
                obj.save()

            # Notify user
            current_site = get_current_site(request)
            subject = '[{0}] Your suggestion was approved'.format(current_site.name)
            template = 'emails/suggestion_approved.txt'
            data = {
                'satname': obj.satellite.name
            }
            message = render_to_string(template, {'data': data})
            try:
                obj.user.email_user(subject, message, from_email=settings.DEFAULT_FROM_EMAIL)
            except Exception:
                logger.error(
                    'Could not send email to user',
                    exc_info=True
                )

        rows_updated = queryset.count()

        # Print a message
        if rows_updated == 1:
            message_bit = '1 suggestion was'
        else:
            message_bit = '{0} suggestions were'.format(rows_updated)
        self.message_user(request, '{0} successfully approved.'.format(message_bit))

    approve_suggestion.short_description = 'Approve selected suggestions'

    def transmitter_uuid(self, obj):
        try:
            return obj.transmitter.uuid
        except Exception:
            return '-'

    def transmitter_data(self, obj):
        if obj.transmitter:
            redirect_url = reverse('admin:base_transmitter_changelist')
            extra = '{0}'.format(obj.transmitter.pk)
            return '<a href="{0}">Transmitter Initial Data</a>'.format(
                redirect_url + extra)
        else:
            return '-'
    transmitter_data.allow_tags = True


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ('name', 'decoder')


@admin.register(DemodData)
class DemodDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'satellite', 'source', 'observer')
    search_fields = ('transmitter__uuid', 'satellite__norad_cat_id', 'observer')

    def satellite(self, obj):
        return obj.satellite
