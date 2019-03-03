from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.operation import ValidationError
from oda.libs.odb.structures.function import Function
from oda.test.oda_test_case import OdaLibTestCase
from oda.libs.odb.ops.create_function_operation import CreateFunctionOperation

TEST_VMA = 0x12345678
TEST_NAME = "some_func"
TEST_VMA2 = 0x87654321
TEST_NAME2 = "some_func2"

class TestAddFunction(OdaLibTestCase):
    def test_add(self):
        odb_file = OdbFile()
        odb_file.execute(CreateFunctionOperation(TEST_VMA, TEST_NAME))


        self.assertEqual(1, len(odb_file.get_structure_list(Function)))
        f = odb_file.get_structure_list(Function)[0]
        self.assertEqual(TEST_NAME, f.name)

        odb_file.operations[-1].undo(odb_file)

        self.assertEqual(0, len(odb_file.get_structure_list(Function)))

    def test_multiple_add(self):
        odb_file = OdbFile()

        op1 = CreateFunctionOperation(TEST_VMA, TEST_NAME, sym_type='U')
        odb_file.execute(op1)

        op2 = CreateFunctionOperation(TEST_VMA2, TEST_NAME2, sym_type='U')
        odb_file.execute(op2)

        self.assertEqual(2, len(odb_file.get_structure_list(Function)))

        op2.undo(odb_file)
        self.assertEqual(1, len(odb_file.get_structure_list(Function)))
        self.assertEqual(TEST_NAME, odb_file.get_structure_list(Function)[
            0].name)

        op1.undo(odb_file)
        self.assertEqual(0, len(odb_file.get_structure_list(Function)))

    def test_add_same_func_name_fails(self):
        odb_file = OdbFile()

        op1 = CreateFunctionOperation(TEST_VMA, TEST_NAME, sym_type='U')
        odb_file.execute(op1)

        op2 = CreateFunctionOperation(TEST_VMA2, TEST_NAME, sym_type='U')

        self.assertRaises(ValidationError, odb_file.execute, op2)


    def test_add_same_id_fails(self):
        odb_file = OdbFile()

        op1 = CreateFunctionOperation(TEST_VMA, TEST_NAME, sym_type='U')
        odb_file.execute(op1)

        self.assertRaises(ValidationError, odb_file.execute, op1)

    def test_add_bad_vma_fails(self):
        odb_file = OdbFile()

        op1 = CreateFunctionOperation(TEST_VMA, TEST_NAME, sym_type='U')
        odb_file.execute(op1)

        op2 = CreateFunctionOperation(TEST_VMA, TEST_NAME2, sym_type='U')

        self.assertRaises(ValidationError, odb_file.execute, op2)

    def undo_not_last_fails(self):
        odb_file = OdbFile()

        op1 = CreateFunctionOperation(TEST_VMA, TEST_NAME, sym_type='U')
        odb_file.execute(op1)

        op2 = CreateFunctionOperation(TEST_VMA2, TEST_NAME2, sym_type='U')
        odb_file.execute(op2)

        self.assertRaises(Exception, op1.undo, odb_file)
