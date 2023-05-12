from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):

    help = 'Clear the entire cache with: cache.clear()'

    def handle(self, *args, **kwargs):

        try:
            cache.clear()

        except Exception as e:
            self.stderr.write(f'ERROR:\n{e}')

        self.stdout.write('Cache cleared')
