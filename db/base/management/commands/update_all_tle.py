"""SatNOGS DB django management command to update TLE entries"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from django.core.management.base import BaseCommand

from db.base.tasks import update_all_tle


class Command(BaseCommand):
    """django management command to update TLE entries"""
    help = 'Update TLEs for existing Satellites'

    def handle(self, *args, **options):
        update_all_tle()
