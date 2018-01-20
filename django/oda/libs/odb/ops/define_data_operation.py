import logging
from oda.libs.odb.disassembler.ofd import Ofd
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.defined_data import DefinedData, DefinedDataList
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.c_struct import CStruct
from oda.libs.odb.structures.types import BuiltinType, BuiltinTypeNames, BuiltinTypeFactory
from oda.libs.odb.ops.operation import ValidationError, Validator
from oda.libs.odb.ops.validators import VmaValidator

logger = logging.getLogger(__name__)

class DefineDataException(ValidationError):
    pass

class DefineDataCollisionException(DefineDataException):
    pass

class DefineDataNotExistException(DefineDataException):
    pass

class NameValidator(Validator):
    def validate(self, operation, odb_file):
        for t in odb_file.get_structure_list(DefinedData):
            if t.var_name == operation.var_name:
                raise ValidationError('Cannot define duplicate name %s' %
                                      operation.var_name)


class TypeKindValidator(Validator):
    def validate(self, operation, odb_file):
        type_kind = operation.type_kind
        type_name = operation.type_name

        supported_type_names = []
        if type_kind == CStruct.kind:
            supported_type_names =\
                [t.name for t in odb_file.get_structure_list(CStruct)]
        elif type_kind == BuiltinType.kind:
            supported_type_names = BuiltinTypeNames()
        else:
            raise ValidationError('Invalid type kind %s' % type_kind)

        if type_name not in supported_type_names:
            raise ValidationError('Invalid type name %s' % type_name)


class FitValidator(Validator):
    def validate(self, operation, odb_file):
        """" Validate the type fits at the given address. """
        vma = operation.vma

        # determine the size of this defined data
        size = operation.size

        # Verify there is not something already defined here
        for dd in odb_file.get_structure_list(DefinedData):
            if dd.overlaps(vma, size):
                raise DefineDataCollisionException(
                        'Data collides with existing data %s' % dd.var_name)

        # Verify there is enough room in the parcel
        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        parcel = parcels.find_parcel_by_vma(vma)

        if not parcel:
            raise ValidationError('Cannot define data at bad address 0x%x' %
                                  vma)
        elif parcel.is_code:
            raise ValidationError('Cannot define data in code region')

        if not parcel.contains_vma(vma + size - 1):
            raise ValidationError('Not enough room to define data')


class DefineDataOperation(Operation):
    """ This operation instantiates a given data type at the specified
    address. """

    def __init__(self, type_kind, type_name, var_name, vma):
        self.object_id = -1
        self.type_kind = type_kind
        self.type_name = type_name
        self.var_name = var_name
        self.vma = vma
        super(DefineDataOperation, self).__init__(
            validators=[NameValidator(), TypeKindValidator()])

    def __str__(self):
        return "Defined data at 0x%x as %s %s %s" % (
            self.vma, self.type_kind, self.type_name, self.var_name)


    @staticmethod
    def deserialize(d):
        op = DefineDataOperation(d['type_kind'],
                                 d['type_name'],
                                 d['var_name'],
                                 d['vma'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'type_kind': self.type_kind,
            'type_name': self.type_name,
            'var_name': self.var_name,
            'vma': self.vma,
        }
        d.update(super().serialize())
        return d

    def instantiate_type(self, type_kind, type_name, odb_file):
        if type_kind == BuiltinType.kind:
            type_inst = BuiltinTypeFactory(type_name)
        elif type_kind == CStruct.kind:
            structs = odb_file.get_structure_list(CStruct)
            type_inst = next(typ for typ in structs if typ.name ==
                             type_name)
        else:
            raise DefineDataException("Invalid type kind %s" % type_kind)

        return type_inst

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        parcels = ParcelList(odb_file.get_structure_list(Parcel))
        parcel = parcels.find_parcel_by_vma(self.vma)
        maxLen = parcel.vma_end - self.vma

        ofd = Ofd(odb_file.binary)
        rawData = ofd.bfd.raw_data(ofd.bfd.sections[parcel.sec_name],
                                   self.vma, maxLen)
        rawData = bytes(rawData)

        # instantiate the type to determine its size
        type_inst = self.instantiate_type(self.type_kind,
                                          self.type_name,
                                          odb_file)

        self.size = type_inst.calc_size(rawData)

        if (self.size <= 0):
            raise DefineDataException("Cannot instantiate empty type")

        try:
            FitValidator().validate(self, odb_file)
        except DefineDataCollisionException as e:
            merged = False
            for dd in odb_file.get_structure_list(DefinedData):
                # find the defined data that overlaps
                if dd.overlaps(self.vma, self.size):
                    # instantiate the class
                    dd_inst = self.instantiate_type(dd.type_kind,
                                                    dd.type_name,
                                                    odb_file)
                    # if we can merge
                    if dd_inst.can_merge(self.type_kind, self.type_name):
                        # delete the data we're going to merge with
                        odb_file.execute(UndefineDataOperation(dd.vma))
                        # run the fit again just to be sure
                        FitValidator().validate(self, odb_file)
                        merged = True

            if not merged:
               raise e

        definedData = odb_file.create_item(DefinedData, {
                'type_kind': self.type_kind,
                'type_name': self.type_name,
                'var_name': self.var_name,
                'vma': self.vma,
                'size': self.size,
            })

        odb_file.insert_item(definedData)

class UndefineDataOperation(Operation):
    """ This operation un-instantiates a given data type at the specified
    address. """

    def __init__(self, vma):
        self.object_id = -1
        self.vma = vma
        super().__init__(
            validators=[VmaValidator()])

    def __str__(self):
        return "Undefined data at 0x%x" % (self.vma)

    @staticmethod
    def deserialize(d):
        op = UndefineDataOperation(d['vma'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):
        self.object_id = odb_file.get_object_id()
        ddl = DefinedDataList(odb_file.get_structure_list(DefinedData))
        dd = ddl.find_by_vma(self.vma)
        if dd:
            odb_file.remove_item(dd)
        else:
            raise DefineDataNotExistException("No defined data at %x" % self.vma)

        # TODO: Update all references to the undefined data
