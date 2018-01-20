import logging

from oda.libs.odb.ops.operation import Validator, ValidationError
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.ops.validators import *

logger = logging.getLogger(__name__)

class CreateCommentOperation(Operation):

    def __init__(self, vma, comment):
        super().__init__(validators=[VmaValidator()])
        self.object_id = -1
        self.vma = vma
        self.comment = comment

    @staticmethod
    def deserialize(d):
        op = CreateCommentOperation(d['vma'], d['comment'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
            'comment': self.comment,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        cmt = odb_file.create_item(Comment, {
            'vma': self.vma,
            'comment': self.comment,
        })

        self.item = cmt

        odb_file.insert_item(cmt)
        return cmt

    def __str__(self):
        return "Created comment '%s' at address 0x%x" % (self.comment, self.vma)

class DeleteCommentOperation(Operation):

    def __init__(self, vma):
        super().__init__(validators=[VmaValidator()])
        self.object_id = -1
        self.vma = vma

    @staticmethod
    def deserialize(d):
        op = DeleteCommentOperation(d['vma'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):
        comments = {c.vma: c for c in odb_file.get_structure_list(Comment)}

        if (self.vma in comments.keys()):
            odb_file.remove_item(comments[self.vma])
        else:
            raise Exception("Cannot delete a comment that does not already "
                            "exist!")

    def __str__(self):
        return "Deleted comment at address 0x%x" % (self.vma)
