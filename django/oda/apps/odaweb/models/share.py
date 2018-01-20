from django.db import models

from oda.apps.odaweb.models import OdaMaster


class Share(models.Model):
    odaMaster = models.ForeignKey(OdaMaster, null=False)
    name = models.CharField(db_index=True, max_length=16)
