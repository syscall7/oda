import os
from oda.libs.odb.binaries import BinaryFile

from oda.libs.odb.odb_file import OdbFile, DefaultOdbSerializer
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.structures.function import Function
from oda.test.oda_test_case import OdaLibTestCase

class TestSerialize(OdaLibTestCase):

    def test_serialize(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        serialized = DefaultOdbSerializer().dumps(odb_file)

        loaded_odb_file = DefaultOdbSerializer().load(serialized)

        self.assertEqual(len(odb_file.get_structure_list(Function)), len(loaded_odb_file.get_structure_list(Function)))



