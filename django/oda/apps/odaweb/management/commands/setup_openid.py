import os
from django.core.management.base import BaseCommand, CommandError
from allauth.socialaccount.models import *
from optparse import make_option

class Command(BaseCommand):
    help = 'Installs Social Account Credentials'

    def handle(self, *args, **options):

        site = Site.objects.get(id=1)
        site.domain="onlinedisassembler.com"
        site.name='onlinedisassembler'
        site.save()

        locations = [
            {
                'name': 'google',
                'client_id': os.environ.get('ODA_OPENID_GOOGLE_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_GOOGLE_SECRET')
            },{
                'name': 'facebook',
                'client_id': os.environ.get('ODA_OPENID_FACEBOOK_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_FACEBOOK_SECRET')
            },{
                'name': 'twitter',
                'client_id': os.environ.get('ODA_OPENID_TWITTER_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_TWITTER_SECRET')
            },{
                'name': 'github',
                'client_id': os.environ.get('ODA_OPENID_GITHUB_CLIENT_ID'),
                'secret': os.environ.get('ODA_OPENID_GITHUB_SECRET')
            }
        ]


        for location in locations:
            try:
                SocialApp.objects.get(provider=location['name'])
                self.stdout.write('%s Already Installed' % (location['name']))
            except SocialApp.DoesNotExist:
                if location['client_id'] and location['secret']:
                    self.stdout.write('Installing provider=%s' % (location['name']))
                    sa = SocialApp(provider=location['name'], name=location['name'],
                               client_id=location['client_id'], secret=location['secret'])
                    sa.save()

                    sa.sites.add(site)

                    sa.save()
