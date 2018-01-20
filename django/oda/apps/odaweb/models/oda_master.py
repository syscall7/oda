import logging
from enum import Enum

from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group, Permission

from bfd import BfdFileFormatException

from oda.apps.odaweb.models import OdaUser
from .sandbox.sandbox_job import SandboxJob

from oda.apps.odaweb.models.binary_file import BinaryFileModel
from oda.apps.odaweb.models.oda_file_storage import OdbFileStorage
from oda.libs.odb.binaries import BinaryString
from oda.libs.odb.odb_file import OdbFile, OdbSerializerV2
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

logger = logging.getLogger(__name__)


class OdbFileLoader(object):
    def load_odb_file(self, oda_master):
        logger.info("load_odb_file odb_master:%s" % oda_master.id)

        if oda_master.odb_file_storage is None:
            return None

        if oda_master.odb_file_storage.pickled_odb_file is None:
            logger.info("Migrating data for %s" % oda_master.id)
            if oda_master.odb_file_storage.binary_file:
                binary_file = oda_master.odb_file_storage.binary_file
                odb_file = OdbFile(BinaryFileModel(binary_file.id))
                odb_file.execute(LoadOperation())
                odb_file.execute(PassiveScanOperation())

                self.store_odb_file(oda_master, odb_file)
            elif oda_master.odb_file_storage.binary_string:
                binary_string = oda_master.odb_file_storage.binary_string
                odb_file = OdbFile(BinaryString(binary_string.binary_string, binary_string.binary_options.architecture))
                odb_file.execute(LoadOperation())
                odb_file.execute(PassiveScanOperation())

                self.store_odb_file(oda_master, odb_file)

            return odb_file

        return OdbSerializerV2().load(
            oda_master.odb_file_storage.pickled_odb_file)

    def store_odb_file(self, oda_master, odb_file):

        logger.info("store_odb_file odb_master:%s %s" % (oda_master.id, type(odb_file.binary)))

        odb_file_storage = oda_master.odb_file_storage
        if odb_file_storage is None:
            odb_file_storage = OdbFileStorage()

        odb_file_storage.pickled_odb_file = OdbSerializerV2().dumps(odb_file)

        if isinstance(odb_file.binary, BinaryFileModel):
            logger.info("uses binary_file_id: %d" % odb_file.binary.binary_file_id)
            odb_file_storage.binary_file_id = odb_file.binary.binary_file_id

        odb_file_storage.save()
        oda_master.odb_file_storage = odb_file_storage


odb_file_system = OdbFileLoader()


class OdaMasterPermissionLevel(Enum):
    none = 10
    read = 20
    edit = 30

class OdaMaster(models.Model):
    """ Complete representation of a disassembled entity """
    class Meta:
        permissions = (
            ("read_odamaster", "Can read this ODA Master"),
            ("edit_odamaster", "Can edit this ODA Master"),
        )

    ipAddress = models.CharField(max_length=64, default='')
    project_name = models.CharField(max_length=64, default='')
    short_name = models.CharField(max_length=12, db_index=True)
    revision = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    copy = models.ForeignKey('OdaMaster', null=True)
    default_permission = models.CharField(max_length=2, default=OdaMasterPermissionLevel.edit.value)
    permissions = models.ManyToManyField(Permission, through='OdaMasterPermission')

    sandbox_job = models.ForeignKey(SandboxJob, null=True)

    odb_file_storage = models.ForeignKey(OdbFileStorage, null=True)

    def __init__(self, *args, **kwargs):
        super(OdaMaster, self).__init__(*args, **kwargs)
        try:
            self._odb_file = odb_file_system.load_odb_file(self)
        except BfdFileFormatException as e:
            self._odb_file = None
            logger.warn("Failed to load odb_file", e)


    def natural_key(self):
        return self.short_name

    @property
    def object_id(self):
        return 0

    @property
    def content_id(self):
        return 0

    @property
    def odb_file(self):
        return self._odb_file

    @odb_file.setter
    def odb_file(self, val):
        self._odb_file = val

    def file_handle(self):
        return self.content_object.file_handle()

    @staticmethod
    def get_by_short_name_and_revision(short_name, revision) -> 'OdaMaster':
        return OdaMaster.objects.get(short_name=short_name, revision=revision)

    @staticmethod
    def get_by_short_name(short_name) -> 'OdaMaster':
        oda_masters = OdaMaster.objects.filter(short_name=short_name).order_by('-creation_date')
        if len(oda_masters) == 0:
            return None
        else:
            return oda_masters[0]

    def next_revision(self):
        revisions = map(lambda m: m.revision, OdaMaster.objects.filter(short_name=self.short_name))
        return max(revisions) + 1

    def latest_revision(self):
        revisions = map(lambda m: m.revision, OdaMaster.objects.filter(short_name=self.short_name))
        return max(revisions)

    def details(self):
        if not self.odb_file:
            return 'UNKNOWN'
        return self.odb_file.get_options().target + " " + self.odb_file.get_options().architecture

    def default_permission_level(self) -> OdaMasterPermissionLevel:
        return OdaMasterPermissionLevel(int(self.default_permission))

    def set_default_permission_level(self, level : OdaMasterPermissionLevel):
        self.default_permission = level.value
        self.save()

    def get_user_permission_level(self, user: OdaUser) -> OdaMasterPermissionLevel:
        if self.owner == user:
            return OdaMasterPermissionLevel.edit

        permissions = self.odamasterpermission_set.filter(user=user) | self.odamasterpermission_set.filter(group=user.groups.all())
        print(permissions)
        permission_level = OdaMasterPermissionLevel.none
        for p in permissions:
            if permission_level == OdaMasterPermissionLevel.edit:
                break
            if p.permission.codename == 'read_odamaster':
                permission_level = OdaMasterPermissionLevel.read
            if p.permission.codename == 'edit_odamaster':
                permission_level = OdaMasterPermissionLevel.edit

        print(permission_level)
        return permission_level if permission_level != OdaMasterPermissionLevel.none else self.default_permission_level()

    def save(self, *args, **kwargs):
        if self._odb_file:
            odb_file_system.store_odb_file(self, self._odb_file)

        super(OdaMaster, self).save(*args, **kwargs)  # Call the "real" save() method.


class OdaMasterPermission(models.Model):
    master = models.ForeignKey(OdaMaster, on_delete=models.CASCADE)
    user = models.ForeignKey(OdaUser, null=True, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

