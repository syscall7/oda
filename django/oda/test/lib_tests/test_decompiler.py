from oda.libs.decompiler import OdaDecompiler, OdaDecompilerException
from oda.test.oda_test_case import OdaLibTestCase
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.binaries import BinaryFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation


class TestDecompiler(OdaLibTestCase):

    def test_decompile_by_addr_good(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        decompiler = OdaDecompiler(odb_file)
        results = decompiler.decompile(0x406b26)
        self.assertEquals(0x4067A0, results.start)
        self.assertEquals(0x406BC0, results.end)
        self.assertNotEquals("", results.source)

    def test_decompile_by_addr_nonexistent(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        decompiler = OdaDecompiler(odb_file)
        with self.assertRaises(OdaDecompilerException):
            decompiler.decompile(0x306b26)
