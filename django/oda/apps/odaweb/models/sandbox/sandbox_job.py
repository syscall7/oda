from django.db import models

from oda.apps.odaweb.models.sandbox.sandbox_server import SandboxServer


class SandboxJob(models.Model):
    """ Represents a sandbox job """
    server = models.ForeignKey(SandboxServer, null=True)
    task_id = models.IntegerField()

    # use to track whether or not we've reloaded the odb file after running the job
    reloaded = models.BooleanField(default=False)
