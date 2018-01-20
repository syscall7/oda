#!/usr/bin/python
import snowman
import binascii
#ret = snowman.decompile("../django/oda/test/test_binaries/ls", 0x406b00, 0x406b35)
ret = snowman.decompile("test_program", 0x40093d, 0x400a05)

if ret:
    print("Decompilation:\n%s" % ret)
elif ret == '':
    print("Decompliation not supported for this function")
