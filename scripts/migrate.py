#!/var/www/oda2/env/bin/python
# -----------------------------------------------------------------------------
# File: uploadReport.py
# Description: Generate a report of what was uploaded in a given day
# Date: 8 November 2011
#
# Last Run Results:
#    Uploaded 74 new files
#    Updated 25663 entries
#    Found 5464 unique files
#    Found 31066 dead entries
#
# Steps before running this script:
#     rsync -a onlinedisassembler.com:/var/oda/uploads/ ./uploads
#     mysqldump -u root -p odapython2 > odapython2.dump
#     mysql -u root -p odapython2 < odapython2.dump
#
# -----------------------------------------------------------------------------
import sys
import os
import glob
from datetime import datetime, date, timedelta
from datetime import time
import time
from subprocess import Popen, PIPE
import hashlib
import MySQLdb

from collections import namedtuple
import sys
import boto
import multiprocessing
import os
import shutil
import StringIO
import tempfile
import threading
import time
import hashlib
from gslib.third_party.oauth2_plugin import oauth2_plugin
from gslib.third_party.oauth2_plugin import oauth2_client

uploaded = 0

def gs_upload(path, filename):

    global uploaded

    # URI scheme for Google Cloud Storage.
    GOOGLE_STORAGE = 'gs'
    BUCKET = 'oda/uploads'
    project_id = 'graphite-tesla-538'

    with open(path, 'rb') as f:
        # Instantiate a BucketStorageUri object.
        uri = boto.storage_uri(BUCKET + '/' + filename, GOOGLE_STORAGE)
        if not uri.exists():
            print 'uploading %s' % path
            uri.new_key().set_contents_from_file(f)
            uploaded += 1

def migrate():

    global uploaded
    conn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = 'password', db = 'odapython2')
    cursor = conn.cursor ()
    cursor.execute('select the_file, id from odaweb_binaryfile')

    rows = cursor.fetchall()
    
    hashes = []
    unique = 0
    updated = 0
    dead = 0
    num_rows = len(rows)
    i = 0
    for row in rows:
        path = os.path.join('/home/anthony', row[0])
        print '%d/%d' % (i, num_rows)

        # if the file exists
        if os.path.exists(path):
            pass
            # sha1
            with open(path, 'rb') as f:
                sha1 = hashlib.md5(f.read()).hexdigest()

            cursor.execute("UPDATE odaweb_binaryfile SET the_file=%s, hash=%s WHERE id=%s", ('uploads/%s' % sha1, sha1, row[1]))
            updated += 1

            if sha1 not in hashes:
                unique += 1
                gs_upload(path, sha1)

            hashes.append(sha1)

        else:
            # delete the odamaster entry and the binaryfile entry            
            dead += 1

        i += 1

    cursor.close()
    conn.commit()
    conn.close()

    print 'Uploaded %d new files' % uploaded
    print 'Updated %d entries' % updated
    print 'Found %d unique files' % unique
    print 'Found %d dead entries' % dead

if __name__ == '__main__':
    try:
      oauth2_client.token_exchange_lock = multiprocessing.Manager().Lock()
    except:
      oauth2_client.token_exchange_lock = threading.Lock()

    migrate()

