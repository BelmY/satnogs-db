"""Django signals for SatNOGS DB"""
import logging

import h5py
from django.db.models.signals import post_save

from db.base.models import Artifact, DemodData, Satellite
from db.base.tasks import decode_current_frame
from db.base.utils import remove_latest_tle_set, update_latest_tle_sets

LOGGER = logging.getLogger('db')


def _remove_latest_tle_set(sender, instance, **kwargs):  # pylint: disable=W0613
    """Updates if needed LatestTle entries"""
    if instance.status in ['re-entered', 'future']:
        remove_latest_tle_set(satellite_id=instance.pk)
    else:
        update_latest_tle_sets(satellite_ids=[instance.pk])


def _extract_network_obs_id(sender, instance, created, **kwargs):  # pylint: disable=W0613
    post_save.disconnect(_extract_network_obs_id, sender=Artifact)
    try:
        with h5py.File(instance.artifact_file, 'r') as h5_file:
            instance.network_obs_id = h5_file.attrs["observation_id"]
    except OSError as error:
        LOGGER.warning(error)

    instance.save()
    post_save.connect(_extract_network_obs_id, sender=Artifact)


def _decode(sender, instance, created, **kwargs):  # pylint: disable=W0613
    """
    Callback function to immediately decode a saved frame
    """
    post_save.disconnect(_decode, sender=DemodData)

    decode_current_frame(instance.satellite.norad_cat_id, instance.id)

    post_save.connect(_decode, sender=DemodData)


post_save.connect(_remove_latest_tle_set, sender=Satellite)

post_save.connect(_decode, sender=DemodData)

post_save.connect(_extract_network_obs_id, sender=Artifact)
