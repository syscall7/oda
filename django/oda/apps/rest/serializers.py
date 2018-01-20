import json
from django.contrib.auth.models import Group
from oda.apps.odaweb.models import OdaUser, OdaMaster
from oda.apps.odaweb.models.oda_master import OdaMasterPermission
from rest_framework import serializers

class OdaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdaUser
        fields = ('username', 'email', 'is_lazy_user')


class UserGroupSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="usergroup-detail")
    users = OdaUserSerializer(source='user_set', many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('url', 'name', 'users')

class CommentSerializer(serializers.Serializer):
    comment = serializers.CharField()
    vma = serializers.IntegerField()

class BinaryFileSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=128)
    filesize = serializers.IntegerField()
    hash = serializers.CharField(max_length=128)

class DataStringSerializer(serializers.Serializer):
    string = serializers.CharField()
    addr = serializers.IntegerField()

class BinaryStringSerializer(serializers.Serializer):
    binary_string = serializers.CharField()

class SymbolSerializer(serializers.Serializer):
    name = serializers.CharField()
    vma = serializers.IntegerField()
    type = serializers.CharField()

class BranchSerializer(serializers.Serializer):
    srcAddr = serializers.IntegerField()
    targetAddr = serializers.IntegerField()

class LabelSerializer(serializers.Serializer):
    label = serializers.CharField()
    vma = serializers.IntegerField()

class OdaMasterPermissionSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_user')
    usergroup = serializers.SerializerMethodField('get_group')
    permission = serializers.SerializerMethodField()

    def get_user(self, permission):
        return permission.user.username if permission.user else None

    def get_group(self, permission):
        return permission.group.name if permission.group else None

    def get_permission(self, permission):
        return str.replace(permission.permission.codename, '_odamaster', '')

    class Meta:
        model = OdaMasterPermission
        fields = ('username', 'usergroup', 'permission')

class OdaMasterPermissionLevelSerializer(serializers.Serializer):
    name = serializers.CharField()

class OdaMasterSerializer(serializers.HyperlinkedModelSerializer):
    permissions = OdaMasterPermissionSerializer(source='odamasterpermission_set', many=True, read_only=True)

    class Meta:
        model = OdaMaster
        fields = ('project_name', 'short_name', 'default_permission_level', 'revision', 'creation_date', 'permissions')

    default_permission_level = OdaMasterPermissionLevelSerializer()

class FunctionSerializer(serializers.Serializer):
    retval = serializers.CharField(required=False)
    args = serializers.CharField()
    vma = serializers.IntegerField()
    name = serializers.CharField()

class CStructFieldTypeSerializer(serializers.Serializer):
    """The types that can be used as fields in a structure"""
    kind = serializers.CharField()      # builtin or cstruct
    name = serializers.CharField()      # name of the type (i.e., uint32_t)
    size = serializers.IntegerField()   # size of the type

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    is_lazy_user = serializers.BooleanField()
    last_login = serializers.DateTimeField()
    email = serializers.CharField()
    date_joined = serializers.DateTimeField

class CStructFieldSerializer(serializers.Serializer):
    """The fields of a specific struct type"""
    name = serializers.CharField()      # name of the field (i.e., field_0)
    kind = serializers.CharField()      # builtin or cstruct
    type = serializers.CharField(source='oda_type.name') # type (i.e., uint32_t)
    size = serializers.IntegerField()

class CStructSerializer(serializers.Serializer):
    name = serializers.CharField()
    is_packed = serializers.BooleanField()
    fields = CStructFieldSerializer(required=False, many=True)
    object_id = serializers.IntegerField()

class DefinedDataSerializer(serializers.Serializer):
    type_kind = serializers.CharField()
    type_name = serializers.CharField()
    var_name = serializers.CharField()
    vma = serializers.IntegerField()
    size = serializers.IntegerField()

class ParcelSerializer(serializers.Serializer):
    vma_start = serializers.IntegerField()
    vma_end = serializers.IntegerField()
    lda_start = serializers.IntegerField()
    is_code = serializers.BooleanField()

class RefSerializer(serializers.Serializer):
    vma = serializers.IntegerField()

class DisplayUnitSerializer(serializers.Serializer):
    section_name = serializers.CharField()
    vma = serializers.IntegerField()
    rawBytes = serializers.CharField()
    instStr = serializers.CharField()
    branch = serializers.CharField()
    branch_label = serializers.CharField()
    opcode = serializers.CharField()
    operands = serializers.CharField()
    stringRef = RefSerializer(required=False)
    branchRef = RefSerializer(required=False)
    targetRef = RefSerializer(required=False)
    crossRef = RefSerializer(required=False, many=True)
    isBranch = serializers.BooleanField()
    isFunction = serializers.BooleanField()
    labelName = serializers.CharField()
    isCode = serializers.BooleanField()

class SectionFlagSerializer(serializers.Serializer):
    abbrev = serializers.CharField()
    desc = serializers.CharField()
    name = serializers.CharField()

class OperationsSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    user = OdaUserSerializer()
    name = serializers.CharField(source='opname')
    desc = serializers.CharField()

class SectionSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.IntegerField()
    vma = serializers.IntegerField()
    flags = SectionFlagSerializer(many=True)
    #alignment_base = serializers.IntegerField()
    #alignment_exp = serializers.IntegerField()

    def restore_fields(self, data, files):
        pass
    def restore_object(self, attrs, instance=None):
        pass

class StringSerializer(serializers.Serializer):
    addr  = serializers.CharField()
    string = serializers.CharField()

class FindResultsSerializer(serializers.Serializer):
    addr  = serializers.IntegerField()
    section = serializers.CharField()
