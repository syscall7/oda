from django.core.management import BaseCommand
from oda.libs.odb.odb_file import BinaryFile, OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation


class Command(BaseCommand):
    args = '<file> <target> <architecture>'
    help = 'Disassemble File ODA'

    def handle(self, *args, **options):

        binary_file = BinaryFile(args[0], args[1], args[2])
        odb_file = OdbFile(binary_file)
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())