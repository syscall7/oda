import logging
import pickle as cPickle
import types
import zlib

from oda.libs.odb.ops.operation import ValidationError
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.label import Label
from oda.libs.odb.structures.c_struct import CStruct
from oda.libs.odb.structures.defined_data import DefinedData
from oda.libs.odb.binaries import Binary, BinaryFile, BinaryString

from oda.apps.odaweb.models.binary_file import BinaryFileModel

from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.ops.active_scan_operation import *
from oda.libs.odb.ops.branch_operations import *
from oda.libs.odb.ops.comment_operations import *
from oda.libs.odb.ops.create_function_operation import *
from oda.libs.odb.ops.cstruct_operations import *
from oda.libs.odb.ops.define_data_operation import *
from oda.libs.odb.ops.idb_import_operation import *
from oda.libs.odb.ops.label_operations import *
from oda.libs.odb.ops.load_operation import *
from oda.libs.odb.ops.modify_settings import *
from oda.libs.odb.ops.passive_scan_operation import *
from oda.libs.odb.ops.split_parcel_operation import *

logger = logging.getLogger(__name__)

STRUCTURE_TYPES = [
    Function, Section, Symbol, Parcel, Branch, DataString, Comment, Label,
    CStruct, DefinedData,
]

OPERATIONS = {cls.__name__: cls for cls in Operation.__subclasses__()}

def DeserializeBinary(d):
    if d['kind'] == 'file':
        return BinaryFile.deserialize(d)
    elif d['kind'] == 'string':
        return BinaryString.deserialize(d)
    elif d['kind'] == 'file_model':
        return BinaryFileModel.deserialize(d)
    else:
        raise Exception("Unrecognized binary kind %s" % d['kind'])


def DeserializeOperation(d):
    cls = d['op_name']
    return OPERATIONS[cls].deserialize(d)


class OdaObjectFactory(object):
    def __init__(self, oda_file):
        self.oda_file = oda_file

    def create(self, class_type, parameters):
        for t in STRUCTURE_TYPES:
            if issubclass(class_type, t):
                return class_type(self.oda_file.get_object_id(), **parameters)
        raise Exception(repr(object) + ' Not Found')


class OdbFile(object):
    def __init__(self, binary=None):

        if binary:
            assert (hasattr(binary, 'file_handle'))
            assert (type(getattr(binary, 'file_handle')) == types.MethodType)

        self.binary = binary
        self.object_id = 0
        self.factory = OdaObjectFactory(self)
        self.operations = []
        self._items = {k.__name__: [] for k in STRUCTURE_TYPES}

    def __str__(self):
        return "OdbFile binary:%s" % self.binary


    @staticmethod
    def deserialize(d):

        binary = DeserializeBinary(d['binary'])
        odb_file = OdbFile(binary)
        odb_file.object_id = d['object_id']

        # TODO: serialize/deserialize the operations instead of pickling
        odb_file.operations = d['operations']

        # deserialize all the items by type
        for stype in STRUCTURE_TYPES:
            if stype.__name__ in d['items']:
                for sitem in d['items'][stype.__name__]:
                    ditem = stype.deserialize(sitem)
                    odb_file.insert_item(ditem)

        operations = []
        for sop in d['operations']:
            operations.append(DeserializeOperation(sop))
        odb_file.operations = operations

        return odb_file


    def serialize(self):

        sitems = {}
        for stype in STRUCTURE_TYPES:
            sitems[stype.__name__] = []
            for ditem in self._items[stype.__name__]:
                sitems[stype.__name__].append(ditem.serialize())

        sops = []
        for op in self.operations:
            d = op.serialize()
            d['op_name'] = op.__class__.__name__
            sops.append(d)

        d = {
            'object_id': self.object_id,
            'binary': self.binary.serialize(),

            # TODO: serialize/deserialize the operations instead of pickling
            'operations': sops,

            'items': sitems,
        }
        return d

    def create_item(self, class_type, parameters):
        return self.factory.create(class_type, parameters)

    def insert_item(self, item):
        #TODO check that the item being added doesn't dupe an ID
        self._items[item.item_type].append(item)
        return item

    def remove_item(self, item):
        self._items[item.item_type].remove(item)

    def get_structure_list(self, class_type):
        return self._items[class_type.__name__]

    def get_arch(self):
        return self.binary.options.architecture

    def execute(self, operation):

        operation.validate(self)

        result = operation.operate(self)

        dup_op = next((op for op in self.operations if op.object_id == operation.object_id), None)
        if dup_op:
            raise ValidationError('Duplicate Operation')

        self.operations.append(operation)

        return result


    def modify_item(self, item):
        for n, i in enumerate(self._items[item.item_type]):
            if n == item:
                self._items[item.item_type][i] = item
                break

    def get_object_id(self):
        self.object_id += 1
        return self.object_id

    def get_options(self):
        return self.binary.options

    def get_binary(self):
        assert (self.binary is not None)

        return self.binary


class DefaultOdbSerializer(object):
    def dumps(self, odb_file):
        return zlib.compress(cPickle.dumps({
            'version': 1,
            'odb_file': odb_file
        }))

    def load(self, serialized):
        if serialized == '':
            return None

        p = zlib.decompress(serialized)
        with open("/tmp/pickled", "wb") as f:
            f.write(p)
        return cPickle.loads(p, encoding='latin1' )['odb_file']

class OdbSerializerV2(object):
    def dumps(self, odb_file):
        return zlib.compress(cPickle.dumps({
            'version': 2,
            'odb_file': odb_file.serialize()
        }))

    def load(self, serialized):
        if serialized == '':
            return None

        p = zlib.decompress(serialized)
        with open("/tmp/pickled", "wb") as f:
            f.write(p)
        unpickled = cPickle.loads(p, encoding='latin1' )
        return OdbFile.deserialize(unpickled['odb_file'])

def scan():
    import pkgutil
    import sys

    modules = pkgutil.iter_modules(path=["odb/structures"])
    for loader, mod_name, ispkg in modules:
        loader.find_module(mod_name).load_module(mod_name)

    [x for x in sys.modules.iterkeys() if x.startswith('odb')]
