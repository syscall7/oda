# Generate a CSV file of user email addresses for MailChimp
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

def export_users(path):

    with open(path, 'wb') as csvfile:
        # TODO: Deal with unicode in first/last names
        #fieldnames = ['email', 'first_name', 'last_name']
        fieldnames = ['email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for user in User.objects.values():
            # catch unicode encoding errors
            try:
                writer.writerow(user)
            except Exception as e:
                print 'Skipping user %s' % user['username']

class Command(BaseCommand):
    args = 'path=<file.csv>'
    help = 'Example: ./migrate.py export_users'

    def handle(self, *args, **options):
        path = args[0]
        export_users(path)

