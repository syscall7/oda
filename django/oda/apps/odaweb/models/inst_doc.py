from django.db import models


class InstDoc(models.Model):
    """ Help for an assembly instruction """
    platform = models.TextField()
    mnemonic = models.TextField()
    short = models.TextField()
    long = models.TextField()
