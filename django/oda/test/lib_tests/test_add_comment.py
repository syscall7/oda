from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.comment_operations import CreateCommentOperation
from oda.libs.odb.structures import comment
from oda.libs.odb.structures.comment import Comment
from oda.test.oda_test_case import OdaLibTestCase

class TestAddFunction(OdaLibTestCase):
    def test_add(self):

        odb_file = OdbFile()

        odb_file.execute(CreateCommentOperation(123, 'This is a comment'))

        self.assertEquals(1, len(odb_file.get_structure_list(Comment)))

