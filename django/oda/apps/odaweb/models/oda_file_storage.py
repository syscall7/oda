from django.db import models

from oda.apps.odaweb.models import BinaryStringStorage, BinaryFile


class OdbFileStorage(models.Model):
    binary_file = models.ForeignKey(BinaryFile, null=True)
    binary_string = models.ForeignKey(BinaryStringStorage, null=True)

    pickled_odb_file = models.BinaryField(null=True, blank=False)
