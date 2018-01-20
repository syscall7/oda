import os
from django.core.management.base import BaseCommand, CommandError
from oda.apps.odaweb.models import OdaUser

class Command(BaseCommand):
    help = 'Setup ODA User Account'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('username', help='Username to create or update')

        # Named (optional) arguments
        parser.add_argument(
            '--superuser',
            action='store_true',
            dest='superuser',
            help='Sets user to be a system superuser',
        )
        parser.add_argument(
            '--password',
            default='password',
            dest='password',
            help='Sets user password',
        )

    def handle(self, *args, **options):
        user, created = OdaUser.objects.get_or_create(username=options['username'])
        if user.password is None or options['password'] != 'password':
            user.set_password(options['password'])
        user.is_superuser = options['superuser']
        user.save()
        if created:
            print("Successfully created user " + user.username)
        else:
            print("Updated user " + user.username)
