from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.structures import c_struct
from oda.libs.odb.structures.c_struct import CStruct, BuiltinField, CStructField
from oda.libs.odb.structures.types import BuiltinTypeFactory
from oda.test.oda_test_case import OdaLibTestCase
from oda.libs.odb.ops.cstruct_operations import CreateCStructOperation, ModifyCStructOperation

class TestAddCStruct(OdaLibTestCase):
    def test_add(self):

        odb_file = OdbFile()

        item = odb_file.execute(CreateCStructOperation('simpleStruct', True))

        builtin = BuiltinTypeFactory('uint8_t')
        item.append_field( BuiltinField(name='Field1',oda_type=builtin) )
        item.append_field( BuiltinField(name='Field2',oda_type=builtin) )
        item.append_field( BuiltinField(name='Field3',oda_type=builtin) )

        self.assertEquals(3, item.size)

        self.assertEquals(1, len(odb_file.get_structure_list(CStruct)))

    def test_compound_add(self):

        odb_file = OdbFile()

        item = odb_file.execute(CreateCStructOperation('simpleStruct', True))
        field_names = ['Field1', 'Field2', 'Field3']
        field_types = ['uint8_t'] * 3
        item = odb_file.execute(ModifyCStructOperation('simpleStruct',
                                                       field_names,
                                                       field_types))


        item2 = odb_file.execute(CreateCStructOperation('complexStruct', True))
        field_names = ['Field1', 'Field3']
        field_types = ['uint8_t', 'simpleStruct']
        item2 = odb_file.execute(ModifyCStructOperation('complexStruct',
                                                       field_names,
                                                       field_types))

        struct_list = odb_file.get_structure_list(CStruct)
        self.assertEquals(2, len(struct_list))
        self.assertEquals(4, struct_list[1].size)

        # delete field from simpleStruct
        field_names = ['Field1', 'Field3']
        field_types = ['uint8_t'] * 2
        item = odb_file.execute(ModifyCStructOperation('simpleStruct',
                                                       field_names,
                                                       field_types))


        struct_list = odb_file.get_structure_list(CStruct)
        sizeLen = struct_list[1].size
        self.assertEquals(3, sizeLen )

