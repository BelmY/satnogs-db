"""SatNOGS DB django base Forms class"""
from bootstrap_modal_forms.forms import BSModalModelForm
from django.core.exceptions import ValidationError
from django.forms import NumberInput, TextInput
from django.utils.translation import ugettext_lazy as _

from db.base.models import Satellite, Transmitter, TransmitterEntry


def existing_uuid(value):
    """ensures the UUID is existing and valid"""
    try:
        Transmitter.objects.get(uuid=value)
    except Transmitter.DoesNotExist:
        raise ValidationError(
            _('%(value)s is not a valid uuid'),
            code='invalid',
            params={'value': value},
        )


class TransmitterModelForm(BSModalModelForm):  # pylint: disable=too-many-ancestors
    """Model Form class for TransmitterEntry objects"""
    class Meta:
        model = TransmitterEntry
        # yapf: disable
        fields = [
            'description', 'type', 'status', 'uplink_low', 'uplink_high', 'uplink_drift',
            'uplink_mode', 'downlink_low', 'downlink_high', 'downlink_drift',
            'downlink_mode', 'invert', 'baud', 'citation', 'service', 'coordination',
            'coordination_url'
        ]
        # yapf: enable
        labels = {
            'downlink_low': _('Downlink freq.'),
            'uplink_low': _('Uplink freq.'),
            'invert': _('Inverted Transponder?'),
        }
        widgets = {
            'description': TextInput(),
        }


class TransmitterUpdateForm(BSModalModelForm):  # pylint: disable=too-many-ancestors
    """Model Form class for TransmitterEntry objects"""
    class Meta:
        model = TransmitterEntry
        # yapf: disable
        fields = [
            'description', 'type', 'status', 'uplink_low', 'uplink_high', 'uplink_drift',
            'uplink_mode', 'downlink_low', 'downlink_high', 'downlink_drift',
            'downlink_mode', 'invert', 'baud', 'citation', 'service', 'coordination',
            'coordination_url', 'created'
        ]
        # yapf: enable
        labels = {
            'downlink_low': _('Downlink freq.'),
            'uplink_low': _('Uplink freq.'),
            'invert': _('Inverted Transponder?'),
            'created': _('Updated'),
        }
        widgets = {
            'description': TextInput(),
            'created': TextInput(attrs={'readonly': True}),
        }


class SatelliteModelForm(BSModalModelForm):
    """Form that uses django-bootstrap-modal-forms for satellite editing"""
    class Meta:
        model = Satellite
        fields = [
            'norad_cat_id', 'name', 'names', 'operator', 'status', 'description', 'countries',
            'website', 'dashboard_url', 'launched', 'deployed', 'decayed', 'image'
        ]
        labels = {
            'norad_cat_id': _('Norad ID'),
            'names': _('Other names'),
            'countries': _('Countries of Origin'),
            'launched': _('Launch Date'),
            'deployed': _('Deploy Date'),
            'decayed': _('Re-entry Date'),
            'description': _('Description'),
            'dashboard_url': _('Dashboard URL'),
            'operator': _('Owner/Operator'),
        }
        widgets = {'norad_cat_id': NumberInput(attrs={'readonly': True}), 'names': TextInput()}
