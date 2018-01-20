from oda.libs.odb.structures.oda_object import OdaObject

class SectionFlag(object):
    def __init__(self, name, abbrev, desc):
        self.name = name
        self.abbrev = abbrev
        self.desc = desc

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @staticmethod
    def deserialize(d):
        return SectionFlag(d['name'],
                           d['abbrev'],
                           d['desc'])

    def serialize(self):
        d = {
            'name': self.name,
            'abbrev': self.abbrev,
            'desc': self.desc,
        }
        return d

class Section(OdaObject):
    def __init__(self, object_id, name, size, vma, flags):
        super(Section, self).__init__(object_id)
        self.name = name
        self.size = size
        self.vma = vma
        self.flags = [SectionFlag(f.name, f.abbrev, f.desc) for f in flags]

    @staticmethod
    def deserialize(d):
        return Section(d['object_id'],
                       d['name'],
                       d['size'],
                       d['vma'],
                       [SectionFlag.deserialize(f) for f in d['flags']])

    def serialize(self):
        d = {
            'object_id': self.object_id,
            'name': self.name,
            'size': self.size,
            'vma': self.vma,
            'flags': [f.serialize() for f in self.flags],
        }
        return d

    def is_loadable(self):
        names = [f.name for f in self.flags]
        return set(['SEC_LOAD']).issubset(names)

