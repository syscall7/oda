import logging

from oda.libs.odb.ops.operation import Validator, ValidationError
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.c_struct import CStruct, BuiltinField, \
    CStructField, Field
from oda.libs.odb.ops.validators import *
from oda.libs.odb.structures.types import BuiltinTypeFactory

logger = logging.getLogger(__name__)

class FieldsValidator(object):
    def validate(self, operation, odb_file):
        for (field_type, field_name) in zip(
                operation.field_types, operation.field_names):
            field = instantiate_field(odb_file, field_type, field_name)
            if not field:
                raise ValidationError("Field is not a valid type")

def instantiate_field(odb_file, field_type, field_name):

    struct_list = odb_file.get_structure_list(CStruct)

    # Check if the field is a built-in type
    builtin = BuiltinTypeFactory(field_type)
    if (builtin != None):
        return BuiltinField(name=field_name, oda_type=builtin)
    else:
        # Check if the field is an existing c_struct
        for struct in struct_list:
            if struct.name == field_type:
                return CStructField(name=field_name, oda_type=struct)

    return None

class CreateCStructOperation(Operation):

    def __init__(self, name, is_packed):
        super().__init__(validators=[])
        self.object_id = -1
        self.name = name
        self.is_packed = is_packed

    def __str__(self):
        return "Created structure %s" % self.name

    @staticmethod
    def deserialize(d):
        op = CreateCStructOperation(d['name'], d['is_packed'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'name': self.name,
            'is_packed': self.is_packed,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        item = odb_file.create_item(CStruct, {
            'name': self.name,
            'is_packed': self.is_packed
        })

        odb_file.insert_item(item)
        return item

    def __str__(self):
        return "Created CStruct '%s'" % (self.name)

class ModifyCStructOperation(Operation):

    def __init__(self, name, field_names, field_types):
        super().__init__(validators=[FieldsValidator()])
        self.object_id = -1
        self.name = name
        self.field_names = field_names
        self.field_types = field_types

    def __str__(self):
        return "Modified structure %s" % self.name

    @staticmethod
    def deserialize(d):
        op = ModifyCStructOperation(d['name'], d['field_names'],
                                    d['field_types'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'name': self.name,
            'field_names': self.field_names,
            'field_types': self.field_types,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()
        struct_list = odb_file.get_structure_list(CStruct)

        item = None
        for s in struct_list:
            if s.name == self.name:
                item = s
                break
        if not item:
            raise Exception("CStruct %s does not exist" % self.name)

        # Delete existing fields
        for oldfield in item.fields[:]:
            item.delete_field(oldfield.name)

        # Add new ones
        for i in range(len(self.field_names)):

            item.append_field(instantiate_field(odb_file,
                                                self.field_types[i],
                                                self.field_names[i]))

        return item

class DeleteCStructOperation(Operation):

    def __init__(self, name):
        super().__init__(validators=[])
        self.object_id = -1
        self.name = name

    def __str__(self):
        return "Deleted structure %s" % self.name

    @staticmethod
    def deserialize(d):
        op = DeleteCStructOperation(d['name'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'name': self.name,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()
        struct_list = odb_file.get_structure_list(CStruct)

        item = None
        for s in struct_list:
            if s.name == self.name:
                item = s
                break
        if not item:
            raise Exception("CStruct %s does not exist" % self.name)

        # Remove references to the struct in other structs
        for struct in struct_list:
            for field in struct.fields[:]:
                if field.kind == 'cstruct' and field.oda_type == item.name:
                    item.delete_field(field.name)

        odb_file.remove_item(item)

        return item
