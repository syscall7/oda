from oda.libs.odb.structures.oda_object import OdaObject

class Branch(OdaObject):

    def __init__(self, object_id, srcAddr, targetAddr, instrLen):
        super(Branch, self).__init__(object_id)
        self.srcAddr = srcAddr
        self.targetAddr = targetAddr
        self.branchDown = self.srcAddr <= self.targetAddr
        self.startAddr = self.srcAddr if self.branchDown else self.targetAddr
        self.stopAddr = self.targetAddr if self.branchDown else self.srcAddr
        self.span = self.stopAddr - self.startAddr
        self.tag = None
        self.instrLen = instrLen

    @staticmethod
    def deserialize(d):
        return Branch(d['object_id'],
                      d['srcAddr'],
                      d['targetAddr'],
                      d['instrLen'])

    def serialize(self):
        d = {
            'object_id' : self.object_id,
            'srcAddr' : self.srcAddr,
            'targetAddr' : self.targetAddr,
            'instrLen' : self.instrLen
        }
        return d

    def overlaps(self, b):
        ret = False

        if (self.stopAddr > b.startAddr) and (self.startAddr < b.stopAddr):
            ret = True

        return ret

    def isSibling(self, b):
        return self.targetAddr == b.targetAddr

    def spans(self, addr):
        return (addr >= self.startAddr) and (addr <= self.stopAddr)

    def isSource(self, addr):
        return (addr == self.srcAddr)

    def isTarget(self, addr):
        return (addr == self.targetAddr)

    def setTag(self, o):
        self.tag = o

    def getTag(self):
        return self.tag
