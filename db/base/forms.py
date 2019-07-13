"""SatNOGS DB django base Forms class"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from db.base.models import Transmitter, TransmitterEntry


class TransmitterEntryForm(forms.ModelForm):
    """Model Form class for TransmitterEntry objects"""

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

    uuid = forms.CharField(required=False, validators=[existing_uuid])

    class Meta:
        model = TransmitterEntry
        exclude = ['uuid', 'reviewed', 'approved', 'created', 'user']
