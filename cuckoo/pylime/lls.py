#!/usr/bin/python
# List the chunks in a LimeDump file

from pylime import *    

if __name__ == '__main__':

    ld = LimeDump()
    ld.read(sys.argv[1])

    if len(ld.mmap) > 0:
        for (addr, buf) in ld.mmap.iteritems():
            print '0x%x: 0x%x bytes' % (addr, len(buf))
    else:
        print 'No sections found'

