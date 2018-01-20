import os
import subprocess
from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = 'Start All Managed Servers'

    def handle(self, *args, **options):
        # Note that you have to specify path to script
        p = subprocess.Popen(["node", os.path.join(settings.BASE_DIR, '..', '..', 'nodejs/socket_app.js')])
        try:
            from django.core.management.commands.runserver import Command as RunServer
            RunServer().execute(*[], **{})
        finally:
            p.kill()
