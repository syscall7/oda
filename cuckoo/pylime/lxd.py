#!/usr/bin/python
# Print a hexdump of the give LimeDump file

from itertools import izip_longest
from pylime import *    
import string

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

#def print_buf(counter, buf):
#    buf2 = [('%02x' % ord(i)) for i in buf]
#    print '{0}: {1:<39}  {2}'.format(('%07x' % (counter)),
#        ' '.join([''.join(buf2[i:i + 2]) for i in range(0, len(buf2), 2)]),
#        ''.join([c if c in string.printable[:-5] else '.' for c in buf]))

def hexdump(addr, buf, group=2):
    for row in grouper(buf, 16, '\x00'):
        print '{0}: {1}  {2}'.format(
            '0x%016x' % addr,
            ' '.join(['%02x' % ord(row[i]) for i in range(len(row))]),
            ''.join([c if c in string.printable[:-5] else '.' for c in row]))
        addr += 16

if __name__ == '__main__':

    ld = LimeDump()
    ld.read(sys.argv[1])

    if len(ld.mmap) > 0:

        for addr in sorted(ld.mmap.keys()):
            hexdump(addr, ld.mmap[addr])
            print ''
    else:
        print 'No sections found'

