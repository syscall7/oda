import logging

from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.ops.validators import *
from oda.libs.odb.structures.parcel import ParcelList, Parcel

logger = logging.getLogger(__name__)

class PruneBranchesOperation(Operation):

    def __init__(self):
        super().__init__(validators=[])
        self.object_id = -1

    @staticmethod
    def deserialize(d):
        op = PruneBranchesOperation()
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        branches = odb_file.get_structure_list(Branch)
        parcels = ParcelList(filter(lambda p: p.is_code,
                                    odb_file.get_structure_list(Parcel)))

        for b in branches:
            if not parcels.contains_vma(b.srcAddr):
                odb_file.remove_item(b)

    def __str__(self):
        return "Pruned branches from dead code parcels"

