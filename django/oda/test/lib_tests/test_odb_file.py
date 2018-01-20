from bidict import bidict
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.label import Label
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.defined_data import DefinedData
from oda.libs.odb.structures.parcel import DataParcel, CodeParcel
from oda.libs.odb.structures.c_struct import CStruct, CStructField, BuiltinField
from oda.libs.odb.structures.types import *
from oda.test.oda_test_case import OdaLibTestCase

from oda.libs.odb.odb_file import OdbFile, OdbSerializerV2, STRUCTURE_TYPES
from oda.libs.odb.binaries import BinaryFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

class TestOdbFile(OdaLibTestCase):

    def helper_test_serialization(self, cls, d):

        d['object_id'] = 123
        obj = cls.deserialize(d)

        serialized = obj.serialize()

        self.assertDictEqual(
            dict(d),
            serialized)

        deserialized = cls.deserialize(serialized)

        self.assertDictEqual(obj.__dict__, deserialized.__dict__)

    def test_serialize_comment(self):
        self.helper_test_serialization(
            Comment,
            {"vma": 0x12345678,
             "comment": "some comment"})

    def test_serialize_branch(self):

        self.helper_test_serialization(
            Branch,
            {"srcAddr": 0x12345678,
             "targetAddr": 0x87654321,
             "instrLen": 6})

    def test_serialize_label(self):

        self.helper_test_serialization(
            Label,
            {"vma": 0x12345678,
             "label": "some label"})

    def test_serialize_function(self):

        self.helper_test_serialization(
            Function,
            {"name": "some_function",
             "vma": 0x12345678,
             "xrefs": set([]),
             "type": "T",
             "retval": "void",
             "args": "uint8_t a, uint16_t b"})

    def test_serialize_section(self):

        self.helper_test_serialization(
            Section,
            {"name": ".text",
             "size": 12345,
             "vma": 0x928374,
             "flags" : []})

    def test_serialize_symbol(self):

        self.helper_test_serialization(
            Symbol,
            {"name": "some symbol",
             "type": "t",
             "vma": 0x1234,
             "xrefs": set([]),
             "base": 0,
             "value": 0x1234})

    def test_serialize_parcel(self):

        self.helper_test_serialization(
            DataParcel,
            {"vma_start": 0x12345678,
             "vma_end": 0x22345678,
             "sec_name": "some label",
             "type": "data",
             "lda_start": 789,
             "lda_bidict": bidict({0: 123, 1: 456, 2: 789, 3: 101112})})

        self.helper_test_serialization(
            CodeParcel,
            {"vma_start": 0x12345678,
             "vma_end": 0x22345678,
             "sec_name": "some label",
             "type": "code",
             "lda_start": 987,
             "lda_bidict": bidict({0: 123, 1: 456, 2: 789, 3: 101112})})

    def test_serialize_defined_data(self):
        self.helper_test_serialization(
            DefinedData,
            {"vma": 0x12345678,
             "type_kind": "builtin",
             "type_name": "ascii",
             "var_name": "some_str",
             "size": 13})

    def test_serialize_cstruct(self):

        objId = 123
        name = "MyCStructSubordinate"
        isPacked = False
        cstructSub= CStruct(objId, name, isPacked)
        cstructSub.append_field(BuiltinField("a", uint16_t, False))
        cstructSub.append_field(BuiltinField("b", uint32_t, False))

        objId = 456
        name = "MyCStruct"
        isPacked = True
        cstruct = CStruct(objId, name, isPacked)
        cstruct.append_field(BuiltinField("field0", uint8_t, False))
        cstruct.append_field(BuiltinField("field1", uint8_t, False))
        cstruct.append_field(CStructField("field2", cstructSub, False))
        cstruct.append_field(BuiltinField("field3", uint64_t, False))

        serialized = cstruct.serialize()

        newCstruct = CStruct.deserialize(serialized)

        self.assertEqual(cstruct.object_id, newCstruct.object_id)
        self.assertEqual(cstruct.name, newCstruct.name)
        self.assertEqual(cstruct.is_packed, newCstruct.is_packed)
        self.assertEqual(len(cstruct.fields), len(newCstruct.fields))
        self.assertEqual(cstruct.size, newCstruct.size)

        for (expected, actual) in zip(cstruct.fields, newCstruct.fields):
            self.assertEqual(expected.name, actual.name)
            self.assertEqual(expected.oda_type.name, actual.oda_type.name)
            self.assertEqual(expected.oda_type.size, actual.oda_type.size)
            self.assertEqual(expected.is_array, actual.is_array)
            self.assertEqual(expected.array_len, actual.array_len)

    def test_serialize_odb_file(self):

        before = OdbFile(BinaryFile(self.get_test_bin_path('ls'),
                                   'elf64-x86-64', 'i386:x86-64'))
        before.execute(LoadOperation())
        before.execute(PassiveScanOperation())

        sodb_file = before.serialize()

        after = OdbFile.deserialize(sodb_file)
        self.assertIsNotNone(after)

        # verify options
        self.assertEqual(before.binary, after.binary)

        # verify structures
        for stype in STRUCTURE_TYPES:
            self.assertEqual(len(before._items[stype.__name__]),
                             len(after._items[stype.__name__]))
            for b,a in zip(before.get_structure_list(stype),
                           after.get_structure_list(stype)):
                self.assertEqual(b,a)

        # verify operations
        self.assertEqual(len(before.operations),
                         len(after.operations))
        for b,a in zip(before.operations, after.operations):
            self.assertEqual(b.__dict__, a.__dict__)

