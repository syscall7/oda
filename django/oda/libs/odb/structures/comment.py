from oda.libs.odb.structures.oda_object import OdaObject

class Comment(OdaObject):
    def __init__(self, object_id, vma, comment):
        super(Comment, self).__init__(object_id)
        self.vma = vma
        self.comment = comment

    @staticmethod
    def deserialize(d):
        return Comment(d['object_id'],
                       d['vma'],
                       d['comment'])


    def serialize(self):
        d = {
            'object_id': self.object_id,
            'vma': self.vma,
            'comment': self.comment,
        }
        return d
