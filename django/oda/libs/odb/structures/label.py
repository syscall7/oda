from oda.libs.odb.structures.oda_object import OdaObject

class Label(OdaObject):
    def __init__(self, object_id, vma, label):
        super().__init__(object_id)
        self.vma = vma
        self.label = label

    @staticmethod
    def deserialize(d):
        return Label(d['object_id'],
                     d['vma'],
                     d['label'])

    def serialize(self):
        d = {
            'object_id' : self.object_id,
            'vma' : self.vma,
            'label' : self.label,
        }
        return d