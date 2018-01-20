from ctypes import *
import sys

class LimeDump():

    class LimeHeader(Structure):

        def __init__(self, addr=0, buf=''):
            LIME_MAGIC = 0x4c694d45
            LIME_VERSION = 1
            super(self.__class__, self).__init__(LIME_MAGIC, LIME_VERSION, addr, addr + len(buf) - 1, 0)

        _fields_ = [('magic', c_uint),
                    ('version', c_uint),
                    ('start', c_ulonglong),
                    ('end', c_ulonglong),
                    ('reserved', c_ulonglong)]

    def __init__(self):
        # store everything internally as a dictionary
        self.mmap = {}

    def add(self, addr, buf):
        # check if this chunk can be appended to an existing chunk
        for (a,b) in self.mmap.iteritems():
            # if this chunk is contiguous
            if (addr == (a + len(b))):
                self.mmap[a] += buf
                return
        self.mmap[addr] = buf

    def remove(self, addr, size):
        raise Exception('Not implemented yet')

    def write(self, path):
        with open(path, 'wb') as f: 
            for (addr, buf) in self.mmap.iteritems():
                hdr = LimeDump.LimeHeader(addr, buf)
                f.write(hdr)
                f.write(buf)

    def read(self, path):
        with open(path, 'rb') as f: 
            f.seek(0, 2)
            bytesLeft = f.tell()
            f.seek(0)

            while (bytesLeft > sizeof(LimeDump.LimeHeader)):
                lh = LimeDump.LimeHeader()
                f.readinto(lh)
                s = lh.end - lh.start + 1
                buf = f.read(lh.end - lh.start + 1)
                self.add(lh.start, buf)
                bytesLeft -= sizeof(lh) + len(buf)
    
    def ls(self):
        if len(self.mmap) > 0:
            for (addr, buf) in self.mmap.iteritems():
                print '0x%x: 0x%x bytes' % (addr, len(buf))
        else:
            print 'No sections found'

if __name__ == '__main__':
    #dump = LimeDump()
    #dump.add(0x0123456789abcdef, 'a'*0x20)
    #dump.add(0xfedcba9876543210, 'b'*0x20)
    #dump.add(0xfedcba9876543230, 'b'*0x20)
    #dump.write('dump.lime')

    #dump2 = LimeDump()
    #dump2.read('dump.lime')
    #dump2.add(0x33, '33')
    #dump2.write('dump2.lime')

    dump = LimeDump()
    dump.read(sys.argv[1])
    dump.ls()

