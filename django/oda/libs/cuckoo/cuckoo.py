import datetime
import hashlib
import logging
from oda.libs.cuckoo import api

from oda.apps.odaweb.models import BinaryFile, BinaryFileModel, SandboxJob, SandboxServer
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

logger = logging.getLogger(__name__)

def assign_server():
    # TODO: Assign server based on current load
    # for now just return the first server in the database
    return SandboxServer.objects.all()[0]

def submit_job(oda_master):

    sjob = SandboxJob(server=assign_server())

    logger.info('submitting cuckoo job for file %s' % oda_master.odb_file.binary.name)
    sjob.task_id = api.submit_task(
        sjob.server,
        oda_master.odb_file.binary.name,
        oda_master.odb_file.binary.file_handle())

    sjob.save()

    oda_master.sandbox_job = sjob
    oda_master.save()

    return CuckooJob(oda_master)

class CuckooJob(object):

    def __init__(self, oda_master):
        self.oda_master = oda_master

        self.name = oda_master.odb_file.binary.name

        # the persistent model of this job
        self.sjob = oda_master.sandbox_job

        if oda_master.sandbox_job is None:
            raise Exception('oda_master does not have a valid sandbox job')

    def status(self):

        status = api.get_status(self.sjob.server, self.sjob.task_id)

        # if the job completed
        if status['status'] == 'reported':
            # get run-time data from cuckoo and reconstruct the odb_file
            self.reload_odb()

        return status

    def report(self):
        # TODO: Throw error if status != 'reported'
        return api.get_report(self.sjob.server, self.sjob.task_id)

    # internal function to create a new odb_file based on runtime info from cuckoo
    def reload_odb(self):

        if self.sjob.reloaded:
            return
        # ensure we only do this once
        self.sjob.reloaded = True
        self.sjob.save()

        logger.info('Reloading odb for job %s' % self.name)
        orig_binary_file = self.oda_master.odb_file.binary

        # get the procdump file
        f = api.get_procdump(self.sjob.server, self.sjob.task_id)
        f.name = self.oda_master.odb_file.binary.name

        binary_file = BinaryFile.create(f)
        binary_file.save()
        bfm = BinaryFileModel(binary_file.id)
        options = orig_binary_file.options

        # TODO: set the target to a new target type called 'cuckoo' or something and add support in ofd
        options.target = 'lime'
        bfm.options = options

        odb_file = OdbFile(bfm)
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        self.oda_master.odb_file = odb_file
        self.oda_master.save()

