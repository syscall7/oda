from oda.libs.odb.structures.oda_object import OdaObject

class Function(OdaObject):
    def __init__(self, object_id, name, vma, sym_type, xrefs=set([]), retval='unknown', args='unknown'):
        super(Function, self).__init__(object_id)
        self.name = name
        self.vma = vma
        self.xrefs = xrefs
        self.type = sym_type
        self.retval = retval
        self.args = args

    @staticmethod
    def deserialize(d):
        return Function(d['object_id'],
                        d['name'],
                        d['vma'],
                        d['type'],
                        d['xrefs'],
                        d['retval'],
                        d['args'])

    def serialize(self):
        d = {
            'object_id' : self.object_id,
            'name' : self.name,
            'vma' : self.vma,
            'xrefs' : self.xrefs,
            'type' : self.type,
            'retval' : self.retval,
            'args' : self.args,
        }
        return d