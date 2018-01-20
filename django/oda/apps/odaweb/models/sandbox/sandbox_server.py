from django.db import models


class SandboxServer(models.Model):
    """ Represents a sandbox server instance """
    ip = models.CharField(max_length=255)
    port = models.IntegerField()
