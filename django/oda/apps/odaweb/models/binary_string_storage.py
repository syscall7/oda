from django.db import models

from oda.apps.odaweb.models import BinaryOptions


class BinaryStringStorage(models.Model):
    binary_string = models.TextField()
    binary_options = models.OneToOneField(BinaryOptions, null=False)
