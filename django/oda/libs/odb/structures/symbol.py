from oda.libs.odb.structures.oda_object import OdaObject

__author__ = 'davis'

class Symbol(OdaObject):
    def __init__(self, object_id, name, sym_type, vma, xrefs, base, value):
        super(Symbol, self).__init__(object_id)
        self.name = name
        self.type = sym_type
        self.vma = vma
        self.xrefs = set(xrefs)
        self.base = base
        self.value = value

    @staticmethod
    def deserialize(d):
        return Symbol(d['object_id'],
                      d['name'],
                      d['type'],
                      d['vma'],
                      d['xrefs'],
                      d['base'],
                      d['value'])

    def serialize(self):
        d = {
            'object_id': self.object_id,
            'name': self.name,
            'type': self.type,
            'vma': self.vma,
            'xrefs': self.xrefs,
            'base': self.base,
            'value': self.value,
        }
        return d