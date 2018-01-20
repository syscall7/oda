from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.binaries import BinaryFile
from oda.libs.odb.ops.define_data_operation import DefineDataOperation
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.ops.operation import ValidationError
from oda.test.oda_test_case import OdaLibTestCase

class TestDefineData(OdaLibTestCase):
    def test_define_invalid_type_kind(self):

        odb_file = OdbFile()

        with self.assertRaisesMessage(ValidationError, 'Invalid type kind '
                                                       'bad_kind'):
            odb_file.execute(DefineDataOperation('bad_kind', 'uint8_t',
                                                 'foo', 0x123))

    def test_define_invalid_type_name(self):

        odb_file = OdbFile()

        with self.assertRaisesMessage(ValidationError, 'Invalid type name '
                                                       'not_uint8_t'):
            odb_file.execute(DefineDataOperation('builtin', 'not_uint8_t',
                                                 'foo', 0x123))

    def test_define_duplicate_name(self):

        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        # define valid data
        odb_file.execute(DefineDataOperation('builtin', 'uint8_t',
                                             'foo', 0x414141))

        with self.assertRaisesMessage(ValidationError, 'Cannot define '
                                                       'duplicate name foo'):
            odb_file.execute(DefineDataOperation('builtin', 'uint32_t',
                                                 'foo', 0x414243))

    def test_define_data_already_defined_there(self):

        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        # define data taking up multiple bytes
        odb_file.execute(DefineDataOperation('builtin', 'uint32_t',
                                             'foo1', 0x414141))

        # try to define another type within the same range
        with self.assertRaisesMessage(ValidationError, 'Data collides with '
                                                       'existing data foo1'):
            odb_file.execute(DefineDataOperation('builtin', 'uint8_t',
                                                 'foo2', 0x414143))

    def test_define_data_will_not_fit(self):
        """ Attempt to define data beyond scope of data region """

        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        # try to define a uint64_t at the end of the .rodata section
        with self.assertRaisesMessage(ValidationError, 'Not enough room to '
                                                       'define data'):
            odb_file.execute(DefineDataOperation('builtin', 'uint64_t',
                                                 'foo2', 0x417e21))

    def test_define_data_in_code(self):
        """ Attempt to define data within a code region """

        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        # try to define a uint64_t in the .text section
        with self.assertRaisesMessage(ValidationError, 'Cannot define data in '
                                                       'code region'):
            odb_file.execute(DefineDataOperation('builtin', 'uint64_t',
                                                 'foo', 0x403098))

