from django.core.management.base import BaseCommand

from db.base.tasks import update_satellite


class Command(BaseCommand):
    help = 'Updates/Inserts Name for certain Satellites'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('norad_ids', nargs='+', metavar='<norad id>')

    def handle(self, *args, **options):
        for norad_id in options['norad_ids']:
            try:
                update_satellite(int(norad_id), update_name=True, update_tle=False)
            except LookupError:
                self.stderr.write('Satellite {} not found in Celestrak'.format(norad_id))
                continue
