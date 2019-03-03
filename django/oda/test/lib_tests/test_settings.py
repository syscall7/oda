from oda.libs.odb.disassembler.ofd import Ofd
from oda.libs.odb.binaries import BinaryString
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.modify_settings import ModifySettingsFactory
from oda.test.oda_test_case import OdaLibTestCase

class TestSettings(OdaLibTestCase):

    def test_load_and_get(self):

        s = '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1'

        odb = OdbFile(BinaryString(s, 'arm'))
        odb.execute(LoadOperation())

        binary = odb.get_binary()
        options = binary.options

        self.assertEqual("arm", options.architecture)
        self.assertEqual(0, options.base_address)
        self.assertEqual('binary', options.target)

    def test_set(self):

        s = '01 20 40 E2 02 20 61 E0 01 30 D1 E4 00 00 53 E3 02 30 C1 E7 FB FF FF 1A 1E FF 2F E1'

        odb = OdbFile(BinaryString(s, 'arm'))
        odb.execute(LoadOperation())

        modify = ModifySettingsFactory.set_architecture('i386')
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEqual("i386", options.architecture)

        modify = ModifySettingsFactory.set_base_address('1000')
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEqual("1000", options.base_address)

        modify = ModifySettingsFactory.set_endian('BIG')
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEqual("BIG", options.endian)

        modify = ModifySettingsFactory.set_values({'selected_opts': ["intel-mnemonic"]})
        odb.execute(modify)
        binary = odb.get_binary()
        options = binary.options
        self.assertEqual(1, len(options.get_extra_options()))
        self.assertEqual('intel-mnemonic', options.get_extra_options()[0])





