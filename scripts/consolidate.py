#!/usr/bin/python
import sys
import os
import hashlib

def consolidate(directory):
    digests = {}
    excepted = set()

    # first pass
    for fname in os.listdir(directory):
        path = os.path.join(directory, fname)
        if os.path.islink(path):
            path = os.path.realpath(path)
            if path not in excepted:
                print 'first pass, adding %s to excepted' % path
                with open(path, 'r') as f:
                    md5 = hashlib.md5(f.read()).hexdigest()
                excepted.add(path)
                digests[md5] = path
	
    # second pass
    for fname in os.listdir(directory):
        path = os.path.join(directory, fname)
        if path not in excepted and not os.path.islink(path):
            print 'second pass, processing %s' % path
            with open(path, 'r') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            if md5 in digests:
                existing = digests[md5]
                print 'Found %s duplicate of %s' % (path, existing)
                os.unlink(path)
                os.symlink(existing, path)
            else:
                digests[md5] = path

if __name__ == '__main__':
    consolidate(os.path.abspath(sys.argv[1]))

