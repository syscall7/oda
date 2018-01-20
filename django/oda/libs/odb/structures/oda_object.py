from abc import ABC, abstractmethod, abstractstaticmethod, abstractclassmethod

class OdaObject(ABC):

    def __init__(self, object_id):
        self.object_id = object_id

    @property
    def item_type(self):
        return self.__class__.__name__

    @abstractmethod
    def serialize(self):
        """Returns this object as a dictionary appropriate for storing"""
        pass

    @abstractstaticmethod
    def deserialize(dict):
        """Construct an object based on the given dictionary"""
        pass

    def __eq__(self, other):
        return self.__dict__ == other.__dict__



import pkgutil
modules = pkgutil.iter_modules(path=["odb.structures"])
for loader, mod_name, ispkg in modules:
    print(mod_name)