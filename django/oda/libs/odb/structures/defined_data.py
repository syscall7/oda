from oda.libs.odb.structures.oda_object import OdaObject

class DefinedData(OdaObject):
    def __init__(self, object_id, vma, type_kind, type_name, var_name, size):
        super(DefinedData, self).__init__(object_id)
        self.type_kind = type_kind
        self.type_name = type_name
        self.var_name = var_name
        self.vma = vma
        self.size = size

    @staticmethod
    def deserialize(d):
        return DefinedData(d['object_id'],
                           d['vma'],
                           d['type_kind'],
                           d['type_name'],
                           d['var_name'],
                           d['size'])

    def serialize(self):
        d = {
            'object_id' : self.object_id,
            'vma' : self.vma,
            'type_kind' : self.type_kind,
            'type_name' : self.type_name,
            'var_name' : self.var_name,
            'size' : self.size,
        }
        return d

    def contains(self, vma):
        return (vma >= self.vma) and (vma < self.vma + self.size)

    def overlaps(self, vma, size):
        last_byte = vma + size - 1
        if (vma >= self.vma) and (vma < self.vma + self.size):
            return True
        elif (last_byte >= self.vma) and (last_byte < self.vma + self.size):
            return True
        else:
            return False

class DefinedDataList(list):
    """ Represents a set of DefinedData on which to operate as a whole """

    def find_by_vma(self, vma):
        """ Find the DefinedData in this list that contains the given VMA """
        for dd in self:
            if dd.contains(vma):
                return dd

        return None

