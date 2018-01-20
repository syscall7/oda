import logging

from oda.libs.odb.ops.operation import Validator, ValidationError
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.comment import Comment

logger = logging.getLogger(__name__)

class VmaValidator(Validator):
    def validate(self, operation, odb_file):
        # TODO: Validate against parcel ranges
        vma = operation.vma
        if vma < 0: # or greater than max?
            raise ValidationError("VMA not valid on item")

