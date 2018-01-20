from oda.libs.odb.structures.oda_object import OdaObject
from oda.libs.odb.structures.types import BuiltinType, OdaType
from abc import ABC, abstractmethod

class CStructFieldDoesNotExistError(Exception):
    pass


class CStructFieldAlreadyExistsError(Exception):
    pass


class Field(ABC):

    def __init__(self, name, oda_type, is_array=False, array_len=0):
        self.name = name
        self.oda_type = oda_type
        self.is_array = is_array
        self.array_len = array_len

    @property
    @abstractmethod
    def size(self):
        pass

    @property
    @abstractmethod
    def kind(self):
        pass

    @staticmethod
    def deserialize(d):

        if d['kind'] == "builtin":
            cls = BuiltinField
            oda_type = BuiltinType.deserialize(d['oda_type'])
        elif d['kind'] == 'cstruct':
            cls = CStructField
            oda_type = CStruct.deserialize(d['oda_type'])
        else:
            raise Exception("Unexpected field kind %s" % d['kind'])

        return cls(d['name'],
                   oda_type,
                   d['is_array'],
                   d['array_len'])

    def serialize(self):
        d = {
            'name' : self.name,
            'is_array' : self.is_array,
            'array_len' : self.array_len,
        }
        return d

class BuiltinField(Field):
    kind = 'builtin'

    def __init__(self, name, oda_type, is_array=False, array_len=1):
        super(BuiltinField, self).__init__(name,oda_type,is_array,array_len)

    def serialize(self):
        d = super().serialize()
        d['kind'] = 'builtin'
        d['oda_type'] = BuiltinType.serialize(self.oda_type)
        return d

    @property
    def size(self):
        return self.oda_type.size*self.array_len

class CStructField(Field):
    kind = 'cstruct'

    def __init__(self, name, oda_type, is_array=False, array_len=1):
        super(CStructField, self).__init__(name,oda_type,is_array,array_len)

    def serialize(self):
        d = super().serialize()
        d['kind'] = 'cstruct'

        # TODO: Only store the name of the referenced CStruct here,
        # not another copy of the entire thing. This will require a two-stage
        # deserialization approach: one pass to register all CStructs that
        # are not composed of other CStructs, and then a final pass to
        # deserialize compound CStructs that reference other ones.
        d['oda_type'] = self.oda_type.serialize()
        return d

    @property
    def size(self):
        return self.oda_type.size*self.array_len


class CStruct(OdaObject, OdaType):
    kind = 'struct'

    def __init__(self, object_id, name, is_packed=True):
        super(CStruct, self).__init__(object_id)
        self._name = name
        self.fields = []
        self.is_packed = is_packed

    # need this to inherit from OdaType
    def getname(self):  return self._name
    def setname(self, name):  self._name = name
    name = property(getname, setname)

    @staticmethod
    def deserialize(d):
        cstruct = CStruct(d['object_id'],
                          d['name'],
                          d['isPacked'])

        for field in d['fields']:
            cstruct.append_field(Field.deserialize(field))

        return cstruct

    def serialize(self):
        d = {
            'object_id': self.object_id,
            'name': self.name,
            'isPacked': self.is_packed,
            'fields': [field.serialize() for field in self.fields]
        }
        return d

    @property
    def size(self):
        if len(self.fields):
            # TODO: Handle unpacked structs (by architecture type?)
            return sum(field.size for field in self.fields)
        else:
            return 0

    def calc_size(self, rawBytes):
        return self.size

    def append_field(self, new_field):
        # Field name must be unique
        for field in self.fields:
            if field.name == new_field.name:
                raise CStructFieldAlreadyExistsError("Field with name already exists in the struct")
        self.fields.append(new_field)

    def prepend_field(self, new_field):
        self.fields.insert(0,new_field)

    def delete_field(self, name):
        for field in self.fields:
            if field.name == name:
                self.fields.remove(field)

class CStructList(list):
    """ Represents a set of CStructs on which to operate as a whole """

    def find_by_name(self, name):
        """ Find the CStruct with the given name and create an instance """
        for cstruct in self:
            if cstruct.name == name:
                return cstruct

        return None

