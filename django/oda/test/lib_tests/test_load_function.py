import os
from oda.libs.odb.binaries import BinaryFile, BinaryString

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.test.oda_test_case import OdaLibTestCase

class TestLoadOperation(OdaLibTestCase):

    def test_basic_loader(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        self.assertEquals(26, len(odb_file.get_structure_list(Section)))

        self.assertEquals(120, len(odb_file.get_structure_list(Symbol)))

        self.assertEquals(2, len(odb_file.get_structure_list(Function)))

        self.assertEquals(1, len([x for x in odb_file.get_structure_list(Function) if x.name == '_init']))
        self.assertEquals(1, len([x for x in odb_file.get_structure_list(Function) if x.name == '_fini']))

        self.assertEquals(1304, len(odb_file.get_structure_list(DataString)))

        self.assertEquals(1, len([s for s in odb_file.get_structure_list(DataString) if s.value == 'hide-control-chars']))
        self.assertEquals(1, len([s for s in odb_file.get_structure_list(DataString) if s.value == 'error initializing month strings']))

    def test_basic_binary_loader(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls.bin.x86-64'), 'binary', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        self.assertEquals(1, len(odb_file.get_structure_list(Section)))

        self.assertEquals(0, len(odb_file.get_structure_list(Symbol)))

        self.assertEquals(0, len(odb_file.get_structure_list(Function)))

        self.assertEquals(857, len(odb_file.get_structure_list(DataString)))

    def test_load_string(self):

        s = '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3'

        odb_file = OdbFile(BinaryString(s, 'i386'))
        odb_file.execute(LoadOperation())

        passive_scan_operation = PassiveScanOperation()
        odb_file.execute(passive_scan_operation)

        self.assertEqual(1, len(odb_file.get_structure_list(Branch)))
        self.assertEqual(1, len(odb_file.get_structure_list(Parcel)))
        self.assertEqual(0, odb_file.get_structure_list(Parcel)[0].vma_start)
        self.assertEqual(35, odb_file.get_structure_list(Parcel)[0].vma_end)

    def test_hash(self):
        s = '55 31 D2 89 E5 8B 45 08 56 8B 75 0C 53 8D 58 FF 0F B6 0C 16 88 4C 13 01 83 C2 01 84 C9 75 F1 5B 5E 5D C3'

        odb_file = OdbFile(BinaryString(s, 'i386'))
        self.assertEqual('d41d8cd98f00b204e9800998ecf8427e', odb_file.get_binary().md5())
        self.assertEqual('da39a3ee5e6b4b0d3255bfef95601890afd80709', odb_file.get_binary().sha1())

    def test_desc(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        self.assertEqual(8, len(odb_file.get_binary().desc()))

    def test_size(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        self.assertEqual(114032, odb_file.get_binary().size)

        s = '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1'
        odb_file = OdbFile(BinaryString(s, 'arm'))
        self.assertEqual(28, odb_file.get_binary().size)

    def test_load_string_arm(self):

        s = '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1'

        odb_file = OdbFile(BinaryString(s, 'arm'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        self.assertEqual(1, len(odb_file.get_structure_list(Branch)))


