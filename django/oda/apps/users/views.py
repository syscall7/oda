import logging

from django.shortcuts import render
from django.template import Context

from oda.apps.odaweb.models import OdaMaster

logger = logging.getLogger(__name__)


def files(request):
    oda_masters = {
        'user': request.user,
        'masters': OdaMaster.objects.filter(owner=request.user, copy=None).order_by('-creation_date')[:25]
    }
    return render(request, 'files.djhtml', oda_masters)