"""SatNOGS DB celery task workers"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import os

from celery import Celery
from django.conf import settings  # noqa

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'db.settings')

RUN_EVERY_15 = 60 * 15
RUN_HOURLY = 60 * 60
RUN_DAILY = 60 * 60 * 24

APP = Celery('db')

APP.config_from_object('django.conf:settings', namespace='CELERY')
APP.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@APP.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Initializes celery tasks that need to run on a scheduled basis"""
    from db.base.tasks import update_all_tle, background_cache_statistics, decode_recent_data

    sender.add_periodic_task(RUN_DAILY, update_all_tle.s(), name='update-all-tle')

    sender.add_periodic_task(
        RUN_HOURLY, background_cache_statistics.s(), name='background-cache-statistics'
    )

    sender.add_periodic_task(RUN_EVERY_15, decode_recent_data.s(), name='decode-recent-data')
