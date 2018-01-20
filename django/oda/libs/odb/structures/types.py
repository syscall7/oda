from oda.libs.odb.structures.oda_object import OdaObject
from abc import abstractmethod, ABC, abstractstaticmethod
import inspect
import sys

# NOTE: Does not inherit from OdaObject
class OdaType(ABC):

    @property
    @abstractmethod
    def kind(self):
        """ The kind of Type this is """

    @property
    @abstractmethod
    def name(self):
        """ The name of this type """

    @property
    @abstractmethod
    def size(self):
        """ Number of bytes occupied by this type instance """

    @abstractmethod
    def calc_size(self, bytes):
        """ Determine the size of the structure given the raw bytes """

    def can_merge(self, type_kind, type_name):
        """ Determine if this type and the given type can merge """
        # children will have to decide this for themselves, but by default, no
        return False

class EnumType(OdaType):
    kind = "enum"


class BuiltinType(OdaType):
    kind = "builtin"

    @staticmethod
    def serialize(self):
        return self.name

    @staticmethod
    def deserialize(name):
        return BuiltinTypeFactory(name)


class String(BuiltinType):
    """ Parent class for different string types"""

    @property
    def size(self):
        """ String size cannot be known statically """
        return None

class ascii(String):
    name = 'ascii'

    def toStr(self, bytes):
        return bytes.decode("latin-1").split('\x00')[0]

    def format(self, bytes):
        return '"%s",0' % self.toStr(bytes)

    def calc_size(self, bytes):
        return len(self.toStr(bytes))+1

    def can_merge(self, type_kind, type_name):
        return type_kind == 'builtin' and type_name == self.name

class Utf8String(String):
    name = 'unicode'

    def format(self, bytes):
        return bytes.decode("utf-8")

    def calc_size(self, bytes):
        # TODO: Figure out how to determine length of a UTF-8 string
        return len(bytes.decode("utf-8"))


class Integer(BuiltinType):

    @staticmethod
    def from_bytes(bytes):
        # TODO: Handle both little endian and big endian (below assumes big endian)
        return int.from_bytes(bytes, byteorder='big')

    def calc_size(self, bytes):
        return self.size

class SignedInteger(Integer):

    def format(self, bytes):
        return '{0:d}'.format(Integer.from_bytes(bytes[:self.size]))


class UnsignedInteger(Integer):

    def format(self, bytes):
        return '0x{0:0{width}x}'.format(Integer.from_bytes(bytes[:self.size]), width=self.size*2)


# TODO: Fix the name property which is dumb, but matches cstruct objects
class uint8_t(UnsignedInteger):
    name = 'uint8_t'
    size = 1


class uint16_t(UnsignedInteger):
    name = 'uint16_t'
    size = 2


class uint32_t(UnsignedInteger):
    name = 'uint32_t'
    size = 4


class uint64_t(UnsignedInteger):
    name = 'uint64_t'
    size = 8


class int8_t(SignedInteger):
    name = 'int8_t'
    size = 1


class int16_t(SignedInteger):
    name = 'int16_t'
    size = 2


class int32_t(SignedInteger):
    name = 'int32_t'
    size = 4


class int64_t(SignedInteger):
    name = 'int64_t'
    size = 8


def BuiltinTypes():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    clstypes = [cls for name, cls in clsmembers if hasattr(cls,'name') and not
                inspect.isabstract(cls)]
    return clstypes


def BuiltinTypeNames():
    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    typenames = [name for name, cls in clsmembers if hasattr(cls,'name') and
                 not inspect.isabstract(cls)]
    return typenames


def BuiltinTypeFactory(type_name):
    # for now, ignore everything after the colon
    name = 'oda.libs.odb.structures.types'
    try:
        mod = __import__(name)
    except ImportError as e:
        return None

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    try:
        initFunc = getattr(mod, type_name)
    except:
        return None

    return initFunc()
