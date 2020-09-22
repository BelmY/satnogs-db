"""Django signals for SatNOGS DB"""
import logging

import h5py
from django.db.models.signals import post_save, pre_save

from db.base.helpers import gridsquare
from db.base.models import Artifact, DemodData

LOGGER = logging.getLogger('db')


def _gen_observer(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_gen_observer, sender=DemodData)
    try:
        qth = gridsquare(instance.lat, instance.lng)
    except Exception:  # pylint: disable=W0703
        instance.observer = 'Unknown'
    else:
        instance.observer = '{0}-{1}'.format(instance.station, qth)
    instance.save()
    post_save.connect(_gen_observer, sender=DemodData)


def _set_is_decoded(sender, instance, **kwargs):  # pylint: disable=W0613
    """Returns true if payload_decoded has data"""
    instance.is_decoded = instance.payload_decoded != ''


def _extract_network_obs_id(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_extract_network_obs_id, sender=Artifact)
    try:
        with h5py.File(instance.artifact_file, 'r') as h5_file:
            instance.network_obs_id = h5_file.attrs["observation_id"]
    except OSError as error:
        LOGGER.warning(error)

    instance.save()
    post_save.connect(_extract_network_obs_id, sender=Artifact)


pre_save.connect(_set_is_decoded, sender=DemodData)

post_save.connect(_gen_observer, sender=DemodData)

post_save.connect(_extract_network_obs_id, sender=Artifact)
