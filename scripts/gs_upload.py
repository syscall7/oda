#!/usr/bin/python
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

def gs_upload(directory):

    # URI scheme for Google Cloud Storage.
    GOOGLE_STORAGE = 'gs'
    BUCKET = 'oda/uploads'
    project_id = 'graphite-tesla-538'


    for fname in os.listdir(directory):
        path = os.path.join(directory, fname)
        if not os.path.islink(path):

            print 'uploading %s' % path
            with open(path, 'r') as f:
                filename = hashlib.sha1(f.read()).hexdigest()
                f.seek(0)

                # Instantiate a BucketStorageUri object.
                uri = boto.storage_uri(BUCKET + '/' + filename, GOOGLE_STORAGE)
                if not uri.exists()
                    uri.new_key().set_contents_from_file(f)

if __name__ == '__main__':
    try:
      oauth2_client.token_exchange_lock = multiprocessing.Manager().Lock()
    except:
      oauth2_client.token_exchange_lock = threading.Lock()

    gs_upload(os.path.abspath(sys.argv[1]))

