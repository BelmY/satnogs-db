from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from db.base.models import TransmitterEntry, Transmitter


class TransmitterEntryForm(forms.ModelForm):
    def existing_uuid(value):
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
