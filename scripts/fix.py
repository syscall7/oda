#!/usr/bin/python
import sys
import os
import hashlib

def consolidate(directory):
    digests = {}
    for fname in os.listdir(directory):
        path = os.path.join(directory, fname)
	if os.path.islink(path):
		realpath = os.path.realpath(path)
		existing = '/var/oda/uploads/%s' % os.path.basename(realpath)
		print 'Linking %s to %s' % (path, existing)
		os.unlink(path)
		os.symlink(existing, path)
		#with open(path, 'r') as f:
		#    md5 = hashlib.md5(f.read()).hexdigest()
		#if md5 in digests:
		#    existing = digests[md5]
		#    print 'Found %s duplicate of %s' % (path, existing)
		#    os.unlink(path)
		#    os.symlink(existing, path)
		#else:
		#    digests[md5] = path

if __name__ == '__main__':
    consolidate(sys.argv[1])

