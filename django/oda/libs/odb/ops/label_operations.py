import logging

from oda.libs.odb.ops.operation import Validator, ValidationError
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.label import Label
from oda.libs.odb.ops.validators import *

logger = logging.getLogger(__name__)

class CreateLabelOperation(Operation):

    def __init__(self, vma, label):
        super().__init__(validators=[VmaValidator()])
        self.object_id = -1
        self.vma = vma
        self.label = label

    def __str__(self):
        return "Created label '%s' at address 0x%x" % (self.label, self.vma)

    @staticmethod
    def deserialize(d):
        op = CreateLabelOperation(d['vma'], d['label'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
            'label': self.label,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        label = odb_file.create_item(Label, {
            'vma': self.vma,
            'label': self.label,
        })

        self.item = label

        odb_file.insert_item(label)
        return label

