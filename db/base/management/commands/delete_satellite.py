"""SatNOGS DB django management command to delete satellites"""
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from db.base.models import Satellite


class Command(BaseCommand):
    """django management command to delete satellites"""
    help = 'Delete selected Satellites'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('norad_ids', nargs='+', metavar='<norad id>')

    def handle(self, *args, **options):
        for norad_id in options['norad_ids']:
            try:
                Satellite.objects.get(norad_cat_id=norad_id).delete()
                self.stdout.write('Deleted satellite {}.'.format(norad_id))
                continue
            except ObjectDoesNotExist:
                self.stderr.write('Satellite with Identifier {} does not exist'.format(norad_id))
