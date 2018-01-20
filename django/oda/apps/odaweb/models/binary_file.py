import logging

import os
import types
import magic

from django.conf import settings
from django.core.files import File
from django.db import models

from .binary_options import BinaryOptions
from oda.apps.odaweb.utils import sha1_hash_contents, sha1_hash
import oda.libs.odb.binaries as binaries

logger = logging.getLogger(__name__)

# this is where we'll cache the GoogleStorage files locally
LOCAL_CACHE_DIR = os.path.join(settings.MEDIA_ROOT, 'cache')


class BinaryFileModel(binaries.Binary):
    def __init__(self, id):
        self.binary_file_id = id
        self._options = BinaryFile.objects.get(id=self.binary_file_id).options

    @staticmethod
    def deserialize(d):
        return BinaryFileModel(d['id'])

    def serialize(self):
        d = {
            'kind': 'file_model',
            'id' : self.binary_file_id,
        }
        return d

    def file_handle(self):
        return BinaryFile.objects.get(id=self.binary_file_id).file_handle()

    @property
    def options(self):
        return self._options

    @property
    def name(self):
        return os.path.split(BinaryFile.objects.get(id=self.binary_file_id).filename)[-1]

    def idb_file(self):
        return BinaryFile.objects.get(id=self.binary_file_id).idb_file

    def set_the_file(self, f):
        return BinaryFile.objects.get(id=self.binary_file_id).set_the_file(f)

    @property
    def size(self):
        return BinaryFile.objects.get(id=self.binary_file_id).size

    @options.setter
    def options(self, options):
        binary_file = BinaryFile.objects.get(id=self.binary_file_id)
        binary_file.binary_options.target = options.target
        binary_file.binary_options.architecture = options.architecture
        binary_file.binary_options.extra_options = options.get_extra_options()
        binary_file.binary_options.base_address = options.base_address
        binary_file.binary_options.save()
        binary_file.save()
        self._options = binary_file.options
        logger.info("Setting Options...")


class BinaryFile(models.Model):
    """ Represents a disassembled entity that was uploaded as a file """
    the_file = models.FileField(upload_to="uploads")
    idb_file = models.FileField(upload_to="uploads", null=True)
    filename = models.CharField(max_length=255)
    filesize = models.IntegerField()
    hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    local_path = None

    binary_options = models.OneToOneField(BinaryOptions, null=True)

    @property
    def options(self):
        return binaries.Options(self.binary_options.target,
                        self.binary_options.architecture,
                       self.binary_options.base_address, self.binary_options.extra_options)

    def file_handle(self):

        # Add done function to the BinaryFile file object
        def done(self):
            # BinaryFiles need to exist indefinitely. Nothing to do here
            pass

        # if we haven't written the file locally yet
        if not self.local_path:

            self.local_path = os.path.join(LOCAL_CACHE_DIR, self.hash)

            # if the file does not exist locally
            if not os.path.exists(self.local_path):
                logger.info("Writing %s %s " % (self.hash, self.local_path))

                # write it out
                with open(self.local_path, 'wb') as f:
                    self.the_file.open('rb')
                    f.write(self.the_file.read())
                    self.the_file.close()

        # return a reference to the local copy
        f = File(open(self.local_path, 'rb'))
        f.done = types.MethodType(done, f)
        return f

    def name(self):
        return self.filename

    @property
    def size(self):
        return self.filesize

    def set_the_file(self, the_file):
        """ This is only used for file constructed via .idb import """
        self.the_file = the_file
        self.hash = sha1_hash(the_file)
        self.filesize = the_file.size
        self.the_file.open('rb')
        self.save()

    def create_from_byte_array(filename, path, data):
        u = BinaryFile()
        u.filename = filename
        u.hash = sha1_hash_contents(data)

        u.the_file = path
        u.filesize = len(data)

        return u

    def create(f):
        u = BinaryFile()
        u.filename = f.name
        u.hash = sha1_hash(f)
        u.idb_file = None

        f.name = u.hash

        u.the_file = File(f)
        u.the_file.open('rb')
        u.filesize = u.the_file.size

        binary_options = BinaryOptions()
        binary_options.save()
        u.binary_options = binary_options

        return u

    def create_from_idb(f):
        u = BinaryFile()
        u.idb_file = File(f)
        u.idb_file.open('rb')
        u.the_file = None
        u.filesize = 0

        binary_options = BinaryOptions()
        binary_options.save()
        u.binary_options = binary_options

        return u

    def is_live_mode(self):
        return False

    def desc(self):
        if self.idb_file == None:
            if os.name == 'nt':
                line = ''
            else:
                f = self.file_handle()
                with magic.Magic() as m:
                    line = m.id_filename(f.name)
                f.close()
                f.done()
            return line.split(', ')
        else:
            return ["This is an IDA Pro .idb file"]

    create_from_byte_array = staticmethod(create_from_byte_array)
    create = staticmethod(create)
