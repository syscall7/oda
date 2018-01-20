from django.core.management.base import BaseCommand

from oda.apps.odaweb.models import BinaryFile, OdaMaster
from elasticsearch import Elasticsearch

class Command(BaseCommand):
    help = 'Dump Files To Elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument('--host')

    def handle_binary_file(self, binary_file):
        return {
            'type': 'file',
            'filename': binary_file.filename,
            'filesize': binary_file.filesize,
            'hash': binary_file.hash,
            'target': binary_file.binary_options.target,
            'architecture': binary_file.binary_options.architecture,
            'extra_options': str(binary_file.binary_options.extra_options),
            'base_address': binary_file.binary_options.base_address

        }

    def handle(self, *args, **options):

        print('ELASTICSEARCH WRITES %s' % options['host'])

        es = Elasticsearch([options['host']])
        for id in OdaMaster.objects.values_list('id', flat=True).filter(copy=None).order_by('creation_date'):
            oda_master = OdaMaster.objects.get(pk=id)
            odb_file_storage = oda_master.odb_file_storage
            if odb_file_storage:
                doc = {
                    'short_name': oda_master.short_name,
                    'ipAddress': oda_master.ipAddress,
                    'created_at' : oda_master.creation_date
                }
                if odb_file_storage.binary_file:
                    doc.update(self.handle_binary_file(odb_file_storage.binary_file))

                print(oda_master)
                res = es.index(index="oda", doc_type='oda_master', id=oda_master.id, body=doc)

