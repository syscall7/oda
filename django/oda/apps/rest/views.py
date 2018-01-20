import logging

from django.core.files import File
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, Http404
from django.db import transaction
from django.utils.decorators import method_decorator
from lazysignup.decorators import allow_lazy_user

# from rest_framework.decorators import action, link, api_view
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status

from django.contrib.auth.models import Group, Permission

from oda.apps.odaweb.models import OdaUser, OdaMaster, Share
from oda.apps.odaweb.models.oda_master import OdaMasterPermission, OdaMasterPermissionLevel
from oda.apps.odaweb.utils import id_generator
from oda.apps.rest.serializers import \
    UserGroupSerializer, \
    OdaMasterSerializer, \
    OdaMasterPermissionSerializer, \
    SectionSerializer, \
    DisplayUnitSerializer, \
    FindResultsSerializer, \
    CommentSerializer, \
    FunctionSerializer, \
    DataStringSerializer, \
    SymbolSerializer, \
    BranchSerializer, \
    LabelSerializer, \
    ParcelSerializer, \
    CStructSerializer, \
    CStructFieldTypeSerializer, \
    OperationsSerializer, \
    DefinedDataSerializer, UserSerializer
from oda.libs.cuckoo import cuckoo
from oda.libs.decompiler import OdaDecompiler
from oda.libs.odb.disassembler.disassembler import Disassembler, get_supported_archs, \
    get_supported_endians, \
    get_platform_options2
from oda.libs.odb.binaries import BinaryString
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.comment_operations import CreateCommentOperation
from oda.libs.odb.ops.cstruct_operations import CreateCStructOperation, \
    ModifyCStructOperation, DeleteCStructOperation
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.modify_settings import ModifySettingsFactory
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.ops.idb_import_operation import IdbImport, IdbImportOperation
from oda.libs.odb.ops.define_data_operation import DefineDataOperation, UndefineDataOperation
from oda.libs.odb.structures.c_struct import CStruct, BuiltinField, CStructField
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.structures.defined_data import DefinedData
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.label import Label
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.types import BuiltinTypeFactory, BuiltinTypes
from oda.libs.odb.display.branchGraph import BranchGraphView

from oda.libs.services.benign import lookup_benign
from oda.libs.services.malware import lookup_malware


logger = logging.getLogger(__name__)


class OdaRestException(APIException):
    status_code = 400
    default_detail = 'Unable to complete request.'


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        """ This view should return a list of groups for the currently
        authenticated user.
        """
        return OdaUser.objects.all()

    @list_route(methods=['get'])
    @method_decorator(allow_lazy_user)
    def who_am_i(self, request):
        user = request.user
        if not user:
            raise Http404('You are a nobody')
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class UserGroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user groups to be viewed or edited
    """
    serializer_class = UserGroupSerializer

    def get_queryset(self):
        """ This view should return a list of groups for the currently
        authenticated user.
        """
        return self.request.user.groups

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
          group = serializer.save()
          logger.info("Created user group " + str(group))
          self.request.user.groups.add(group)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['post', 'delete'])
    def user(self, request, pk):
        username = self.request.data.get('username')
        if username is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            group = self.request.user.groups.get(pk=pk)
            user = OdaUser.objects.get_by_natural_key(username)
            if request.method == 'POST':
                user.groups.add(group)
                serializer = self.get_serializer(group)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            if request.method == 'DELETE':
                user.groups.remove(group)
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class HasOdaMasterPermission(BasePermission):
    def has_permission(self, request, view):
        if isinstance(view, OdaMasterViewSet):
            # Permission enforcement for OdaMaster listing is done using queryset
            if view.action == 'list':
                return True

        short_name = view.kwargs.get('short_name') or request.query_params.get('short_name') or request.data.get('short_name')
        if short_name is not None:
            oda_master = OdaMaster.get_by_short_name(short_name)
            if oda_master is not None:
                permission_level = oda_master.get_user_permission_level(request.user)
                if permission_level == OdaMasterPermissionLevel.edit:
                    return True
                if permission_level == OdaMasterPermissionLevel.read and request.method == 'GET':
                    return True

                return False

        raise OdaRestException('Bad or missing short_name')


class OdaMasterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user groups to be viewed or edited
    """
    permission_classes = (HasOdaMasterPermission,)
    serializer_class = OdaMasterSerializer
    lookup_field = 'short_name'
    # TODO: Probably need to paginate the queryset, but the front-end needs to support it first..
    # paginate_by = 10

    def get_queryset(self):
        oda_master_permissions = OdaMasterPermission.objects.filter(user=self.request.user) | OdaMasterPermission.objects.filter(group=self.request.user.groups.all())
        oda_masters = OdaMaster.objects.filter(owner=self.request.user) | OdaMaster.objects.filter(pk__in=[m.pk for m in [p.master for p in oda_master_permissions]])
        return oda_masters

    @detail_route(permission_classes=[])
    @method_decorator(allow_lazy_user)
    def can_edit(self, request, **kwargs):
        oda_master = OdaMaster.get_by_short_name(kwargs['short_name'])
        if oda_master == None:
            return Response(status=status.HTTP_404_NOT_FOUND, data='This document cannot be found')
        own = (oda_master.get_user_permission_level(request.user) == OdaMasterPermissionLevel.edit)
        return Response(own)

    @detail_route()
    @method_decorator(allow_lazy_user)
    def clone(self, request, short_name=''):
        from oda.apps.odaweb.views import make_copy
        oda_master = OdaMaster.get_by_short_name(short_name)
        if oda_master.owner == request.user:
            raise OdaRestException("Don't copy an oda_master you already own")
        the_copy = make_copy(oda_master, request.user)
        return Response(the_copy.short_name)

    @detail_route()
    def branches(self, request, **kwargs):
        oda_master = OdaMaster.get_by_short_name(kwargs['short_name'])
        odb_file = oda_master.odb_file
        branches = odb_file.get_structure_list(Branch)
        return Response({'branches': [BranchSerializer(x).data for x in branches]})

    @detail_route(methods=['post'])
    def set_default_permission_level(self, request, **kwargs):
        oda_master = OdaMaster.get_by_short_name(kwargs['short_name'])
        new_permission_level = OdaMasterPermissionLevel[request.data['permission_level']]
        oda_master.set_default_permission_level(new_permission_level)
        return Response({'permission_level': new_permission_level.value})

    @detail_route(methods=['get'])
    def permissions(self, request, **kwargs):
        oda_master = OdaMaster.get_by_short_name(kwargs['short_name'])
        if not oda_master:
            raise OdaRestException('ODA Master ' + kwargs['short_name'] + ' not found.')
        permissions = oda_master.odamasterpermission_set.all()
        serializer = OdaMasterPermissionSerializer(permissions, many=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    @detail_route(methods=['post', 'delete'])
    def permission(self, request, **kwargs):
        permission = self.request.data.get('permission')
        username = self.request.data.get('username')
        usergroup = self.request.data.get('usergroup')
        if permission is None or (username is None and usergroup is None):
            raise OdaRestException('Must specify permission and username or usergroup.')
        oda_master = OdaMaster.get_by_short_name(kwargs['short_name'])
        if not oda_master:
            raise OdaRestException('ODA Master ' + kwargs['short_name'] + ' not found.')
        not_found = None
        try:
            perm = Permission.objects.get(codename=permission + '_odamaster')
            user = OdaUser.objects.get_by_natural_key(username) if username else None
            group = self.request.user.groups.get(name=usergroup) if usergroup else None
            if not user and not group:
                raise OdaRestException('Must specify user or group.')
            args = {'master': oda_master, 'permission': perm}
            if user:
                args['user'] = user
            if group:
                args['group'] = group
            if request.method == 'POST':
                OdaMasterPermission.objects.create(**args)
                serializer = self.get_serializer(oda_master)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            if request.method == 'DELETE':
                OdaMasterPermission.objects.get(**args).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except OdaUser.DoesNotExist:
            not_found = 'User'
        except OdaMasterPermission.DoesNotExist:
            not_found = 'OdaMasterPermission'
        except Group.DoesNotExist:
            not_found = 'Group'
        except Permission.DoesNotExist:
            not_found = 'Permission'
        if not_found:
            raise OdaRestException(not_found + ' not found.')
        raise OdaRestException


class OdaStructureViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)

    def __init__(self, **kwargs):
        super(OdaStructureViewSet, self).__init__(**kwargs)
        self.odb_file = None

    def get_structure_list(self):
        return self.odb_file.get_structure_list(self.structure)

    def map_item(self, item):
        return item

    def list(self, request, format=None):
        short_name = request.query_params.get('short_name', None)
        revision = request.query_params.get('revision', None)

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        self.odb_file = oda.odb_file

        structure_list = self.get_structure_list()
        mapped_structure_list = [self.map_item(i) for i in structure_list]
        serializer = self.get_serializer(mapped_structure_list, many=True)
        return Response(serializer.data)

class OperationsViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)
    serializer_class = OperationsSerializer
    queryset = OdaMaster.objects.all()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.odb_file = None

    def list(self, request, format=None):
        short_name = request.query_params.get('short_name', None)
        revision = request.query_params.get('revision', None)
        oda = self.get_queryset().get(short_name=short_name, revision=revision)
        self.odb_file = oda.odb_file

        serializer = self.get_serializer(self.odb_file.operations, many=True)
        return Response(serializer.data)

class CommentViewSet(OdaStructureViewSet):
    serializer_class = CommentSerializer
    structure = Comment

    def create(self, request):

        logger.info("Creating comment " + str(request))

        comment = request.data['comment']
        vma = int(request.data['vma'])
        short_name = request.data['short_name']
        revision = request.data['revision']

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file

        item = odb_file.execute(CreateCommentOperation(vma, comment))
        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        oda = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])
        odb_file = oda.odb_file
        if request.data.get('vma'):
            vma = request.data.get('vma')
            comments = {c.vma: c for c in odb_file.get_structure_list(Comment)}
            if vma in comments:
                odb_file.remove_item(comments[vma])
                oda.save()
                return Response({}, status=status.HTTP_200_OK)

        return Response({'error': ''}, status=status.HTTP_400_BAD_REQUEST)


class FunctionViewSet(OdaStructureViewSet):
    serializer_class = FunctionSerializer
    structure = Function

    def partial_update(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        error = None
        vma = None
        if request.data.get('vma'):
            vma = request.data.get('vma', 0)

        name = None
        if request.data.get('name'):
            name = request.data.get('name')

        args = None
        if request.data.get('args'):
            args = request.data.get('args')

        retval = None
        if request.data.get('retval'):
            retval = request.data.get('retval')

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.edit_function(vma, name, args, retval)
            oda.save()
        except Exception as e:
            error = e.message
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'function': name,
            'error': error
        })


class SectionsViewSet(OdaStructureViewSet):
    serializer_class = SectionSerializer
    structure = Section

    def get_structure_list(self):
        sections = self.odb_file.get_structure_list(Section)
        return filter(lambda s: s.is_loadable(), sections)


class StringsViewSet(OdaStructureViewSet):
    serializer_class = DataStringSerializer
    structure = DataString

    def map_item(self, item):
        return {
            'string': item.value,
            'addr': item.addr
        }


class LabelsViewSet(OdaStructureViewSet):
    serializer_class = LabelSerializer
    structure = Label


class SymbolsViewSet(OdaStructureViewSet):
    serializer_class = SymbolSerializer
    structure = Symbol

    def get_structure_list(self):
        # NOTE: If there are multiple symbols for the same address, we will ignore all but one of them here when
        #       creating this dictionary.
        sym_dict = {
            sym.vma: sym
            for sym in self.odb_file.get_structure_list(Symbol)
            if (sym.vma != 0)
        }

        return sym_dict.values()


class ParcelsViewSet(OdaStructureViewSet):
    serializer_class = ParcelSerializer
    structure = Parcel

    def get_structure_list(self):
        parcels = self.odb_file.get_structure_list(Parcel)
        return sorted(parcels, key=lambda p: p.vma_start)


class BinaryStringViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)

    def partial_update(self, request, pk):
        oda_master = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        previous_odb = oda_master.odb_file

        try:
            odb_file = OdbFile(
                BinaryString(request.data['binary_string'], previous_odb.get_binary().options.architecture))
            odb_file.execute(LoadOperation())
            odb_file.execute(PassiveScanOperation())
        except (TypeError, UnicodeDecodeError, UnicodeEncodeError):
            return HttpResponseNotAllowed('Invalid hex digits')

        oda_master.odb_file = odb_file
        oda_master.save()

        logger.info("updating...")

        return Response({'binary_string': request.data['binary_string']})


class OptionsViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)

    def partial_update(self, request, pk):
        oda_master = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        arch = request.data.get('architecture')
        ba = request.data.get('base_address', 0)
        base_address = hex(ba) if ba else 0
        endian = request.data.get('endian')
        selected_opts = request.data.get('selected_opts')

        logger.info("updating binary options ..." + str(oda_master))

        odb_file = oda_master.odb_file
        odb_file.execute(ModifySettingsFactory.set_values({
            'architecture': arch,
            'base_address': base_address,
            'endian': endian,
            'selected_opts': selected_opts
        }))

        odb_file = OdbFile(odb_file.binary)

        if odb_file.binary.idb_file():
            idbImport = IdbImport(File(odb_file.binary.idb_file()))
            path = idbImport.reconstruct_elf()
            odb_file.binary.set_the_file(File(open(path, "rb")))
            odb_file.execute(IdbImportOperation())

        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())
        oda_master.odb_file = odb_file
        oda_master.save()

        return Response({'status': 'ok'})


class DisplayUnitsViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)
    serializer_class = DisplayUnitSerializer

    def get_queryset(self):
        pass

    def list(self, request):

        start = 0
        units = 100
        logical = False

        if request.query_params.get('addr'):
            start = int(request.query_params.get('addr'), 0)
        if request.query_params.get('units'):
            units = int(request.query_params.get('units'), 0)
        if request.query_params.get('logical'):
            logical = True  # TODO: Check this value for realz

        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        dasm = Disassembler(oda.odb_file)
        dunits = dasm.display(start, units, logical)

        logger.debug("DisplayUnitsViewSet: Generate serialized data")
        serializer = self.get_serializer(dunits, many=True)
        serialData = Response(serializer.data)
        logger.debug("DisplayUnitsViewSet: Serial data complete")
        return serialData

    @detail_route()
    def size(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        dasm = Disassembler(oda.odb_file)
        return Response(dasm.total_lines())

    @detail_route()
    def vmaToLda(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        dasm = Disassembler(oda.odb_file)
        return Response(dasm.vma_to_lda(vma))

    @detail_route()
    def ldaToVma(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        lda = 0
        if request.query_params.get('lda'):
            lda = int(request.query_params.get('lda'), 0)

        dasm = Disassembler(oda.odb_file)
        return Response(dasm.lda_to_vma(lda))

    @detail_route()
    def makeData(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        error = None
        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.make_data(vma)
        except Exception as e:
            error = str(e)
        oda.save()

        return Response({'error': error})

    @detail_route()
    def makeCode(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                    revision=request.query_params.get('revision'))

        error = None
        vma = 0
        if request.query_params.get('vma'):
            vma = int(request.query_params.get('vma'), 0)

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.make_code(vma)
        except Exception as e:
            raise OdaRestException(e)
        oda.save()

        return Response({'error': error})

    @detail_route(methods=['post'])
    def makeFunction(self, request, pk):
        oda = OdaMaster.objects.get(short_name=request.data.get('short_name'),
                                    revision=request.data.get('revision'))

        error = None
        vma = 0
        if request.data.get('vma'):
            vma = request.data.get('vma')

        name = 'func_%x' % vma
        if request.data.get('name'):
            name = request.data.get('name')

        args = 'unknown'
        if request.data.get('args'):
            args = request.data.get('args')

        retval = 'unknown'
        if request.data.get('retval'):
            retval = request.data.get('retval')

        dasm = Disassembler(oda.odb_file)
        try:
            dasm.make_function(vma, name, args, retval)
            oda.save()
        except Exception as e:
            error = e.message
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'function': name,
            'error': error
        })


class FindViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)
    serializer_class = FindResultsSerializer

    def get_queryset(self):
        pass

    def list(self, request):

        try:
            bytes = self.request.query_params.get('bytes', None)
            oda = OdaMaster.objects.get(short_name=request.query_params.get('short_name'),
                                        revision=request.query_params.get('revision'))

            dasm = Disassembler(oda.odb_file)
            results = [{'addr': key, 'section': value} for key, value in
                       sorted(dasm.find(bytes).items(), key=lambda s: s[0])]
            serializer = self.get_serializer(results, many=True)

        except Exception as e:
            raise OdaRestException(e)

        return Response(serializer.data)


class CStructFieldTypesViewSet(OdaStructureViewSet):
    serializer_class = CStructFieldTypeSerializer
    structure = CStructField

    def get_structure_list(self):
        # Include the built in types
        builtins = [field() for field in BuiltinTypes()]

        # Include c_structs too
        cstructs = self.odb_file.get_structure_list(CStruct)

        return sorted(builtins + cstructs, key=lambda s: type(s).__name__)


class CStructsViewSet(OdaStructureViewSet):
    serializer_class = CStructSerializer
    structure = CStruct

    def get_structure_list(self):
        cstructs = self.odb_file.get_structure_list(CStruct)
        return sorted(cstructs, key=lambda s: s.name)

    def create(self, request):

        logger.info("Creating cstruct " + str(request))

        name = request.data['name']
        is_packed = request.data['is_packed']
        short_name = request.data['short_name']
        revision = request.data['revision']

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        item = oda.odb_file.execute(CreateCStructOperation(name, is_packed))
        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

    @detail_route()
    def modify(self, request, pk):

        logger.info("Modify cstruct " + str(request))

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        field_names = request.query_params.getlist('field_names[]')
        field_types = request.query_params.getlist('field_types[]')

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        struct_list = oda.odb_file.get_structure_list(CStruct)
        name = struct_list[int(pk)].name
        item = oda.odb_file.execute(ModifyCStructOperation(name, field_names,
                                                           field_types))

        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        oda = OdaMaster.objects.get(short_name=request.data['short_name'], revision=request.data['revision'])

        struct_list = oda.odb_file.get_structure_list(CStruct)

        if pk:
            item = struct_list[int(pk)]

            oda.odb_file.execute(DeleteCStructOperation(item.name))
            oda.save()

            return Response({}, status=status.HTTP_200_OK)

        return Response({'error': ''}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def append_field(self, request, pk):

        logger.info("Adding field to cstruct " + str(request))

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        field_name = request.query_params.get('field_name')
        field_type = request.query_params.get('field_type')

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        struct_list = oda.odb_file.get_structure_list(CStruct)
        item = struct_list[int(pk)]

        # Check if the field is a built-in type
        builtin = BuiltinTypeFactory(field_type)
        if (builtin != None):
            item.append_field(BuiltinField(name=field_name, type=builtin))
        else:
            # Check if the field is an existing c_struct
            for struct in struct_list:
                if struct.name == field_type:
                    item.append_field(CStructField(name=field_name, c_struct_obj=struct))

        oda.save()

        serializer = self.get_serializer(item, many=False)
        return Response(serializer.data)

class DefinedDataViewSet(OdaStructureViewSet):
    serializer_class = DefinedDataSerializer
    structure = DefinedData

    def get_structure_list(self):
        dd = self.odb_file.get_structure_list(DefinedData)
        return sorted(dd, key=lambda s: s.type_kind)

    def create(self, request):

        logger.info("Defining data " + str(request))

        short_name = request.data['short_name']
        revision = request.data['revision']

        type_kind = request.data['type_kind']
        type_name = request.data['type_name']
        var_name = request.data['var_name']
        vma = request.data['vma']

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file
        definedData = None

        error = None
        try:
            odb_file.execute(DefineDataOperation(type_kind, type_name, var_name,
                                             vma))
            oda.save()

            item = None
            for dd in odb_file.get_structure_list(DefinedData):
                if dd.type_kind == type_kind and \
                   dd.type_name == type_name and \
                   dd.var_name == var_name and \
                   vma == vma:
                    item = dd
                    break

            serializer = self.get_serializer(item, many=False)
            definedData = serializer.data

        except Exception as e:
            raise OdaRestException(e)

        return Response({
            'definedData': definedData,
        })

    @detail_route()
    def modify(self, request, pk):
        pass

    def destroy(self, request, pk=None):
        logger.info("Undefining data " + str(request))

        short_name = request.data['short_name']
        revision = request.data['revision']

        vma = request.data['vma']

        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file
        definedData = None

        try:
            item = None
            for dd in odb_file.get_structure_list(DefinedData):
                # if this dd overlaps with the given vma
                if dd.overlaps(vma, 1):

                    # delete it
                    odb_file.execute(UndefineDataOperation(vma))
                    oda.save()

                    # return the dd we just deleted
                    serializer = self.get_serializer(item, many=False)
                    definedData = serializer.data
                    break

        except Exception as e:
            raise OdaRestException(e)

        return Response({
            'definedData': definedData,
        })

class SandboxViewSet(viewsets.GenericViewSet):
    permission_classes = (HasOdaMasterPermission,)

    # @action()
    def submit(self, request, pk):
        # disable for now
        return Response(status=status.HTTP_404_NOT_FOUND)

        short_name = request.data.get('short_name')
        revision = request.data.get('revision')
        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        job = cuckoo.submit_job(oda)
        return Response({
            "status": job.status()
        })

    @detail_route()
    def status(self, request, pk):
        # disable for now
        return Response(status=status.HTTP_404_NOT_FOUND)

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        job = cuckoo.CuckooJob(oda)
        return Response({
            "status": job.status(),
        })

    @detail_route()
    def report(self, request, pk):
        # disable for now
        return Response(None)

        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision')
        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        try:
            job = cuckoo.CuckooJob(oda)
            response = Response(job.report())
        except:
            response = Response(None)

        return response


class ODBLoadView(APIView):
    permission_classes = (HasOdaMasterPermission,)

    def get(self, request):
        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision', 0)
        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file
        binary = oda.odb_file.get_binary()
        sym_dict = {
            sym.vma: sym
            for sym in odb_file.get_structure_list(Symbol)
            if (sym.vma != 0)
        }

        branches = odb_file.get_structure_list(Branch)

        live_mode = isinstance(binary, BinaryString)

        symbols = sym_dict.values()

        parcels = sorted(odb_file.get_structure_list(Parcel), key=lambda p: p.vma_start)

        sections = filter(lambda s: s.is_loadable(), odb_file.get_structure_list(Section))

        dasm = Disassembler(odb_file)
        size = dasm.total_lines()

        # Include the built in types
        builtins = [field() for field in BuiltinTypes()]

        # Include c_structs too
        cstructs = odb_file.get_structure_list(CStruct)
        fieldTypes = sorted(builtins + cstructs, key=lambda s: type(
                                s).__name__)

        binary_text = 'N/A'
        if live_mode:
            binary_text = binary.binary_string_display

        return Response({
            'project_name': oda.project_name,
            'binary': {
                'size': int(str(binary.size)),
                'md5': str(binary.md5()),
                'sha1': str(binary.sha1()),
                'desc': binary.desc(),
                'name': binary.name,
                'malware': False, # str(lookup_malware(binary)),
                'benign': True, # str(lookup_benign(binary)),
                'text': binary_text,
                'options': {
                    'architecture': binary.options.architecture,
                    'base_address': binary.options.base_address,
                    'endian': binary.options.endian,
                    'selected_opts': binary.options.selected_opts
                }

            },
            'live_mode': live_mode,
            'functions': [FunctionSerializer(x).data for x in odb_file.get_structure_list(Function)],
            'labels': [LabelSerializer(x).data for x in odb_file.get_structure_list(Label)],
            'sections': SectionSerializer(sections, many=True).data,
            'parcels': [ParcelSerializer(x).data for x in parcels],
            'comments': [CommentSerializer(x).data for x in odb_file.get_structure_list(Comment)],
            'symbols': [SymbolSerializer(x).data for x in symbols],
            'branches': [BranchSerializer(x).data for x in branches],
            'default_permission_level': oda.default_permission_level().name,
            'strings': [DataStringSerializer({
                'string': x.value,
                'addr': x.addr
            }).data for x in odb_file.get_structure_list(DataString)],
            'structTypes': [CStructSerializer(x).data for x in odb_file.get_structure_list(CStruct)],
            'structFieldTypes': [CStructFieldTypeSerializer(x).data for x in
                                 fieldTypes],
            'displayUnits': {
                "size": size
            },
            #TODO Move these elsewhere
            'user': UserSerializer(request.user).data,
            'architectures': get_supported_archs(),
            'endians': [{
                'name': x,
                'intValue': y
            } for x, y in get_supported_endians().items()]
        })


class GraphView(APIView):
    permission_classes = (HasOdaMasterPermission,)

    def get(self, request):
        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision', 0)
        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        odb_file = oda.odb_file
        vma = int(request.query_params.get('addr'))
        try:
            bgv = BranchGraphView(odb_file, vma)

            serialized_nodes = []
            for n in bgv.nodes:
                sn = n
                sn['instructions'] = DisplayUnitSerializer(n['instructions'], many=True).data
                serialized_nodes.append(sn)
            return Response({
                'nodes': serialized_nodes,
                'links': bgv.links,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DecompilerView(APIView):
    def get(self, request):
        short_name = request.query_params.get('short_name')
        revision = request.query_params.get('revision', 0)
        oda = OdaMaster.objects.get(short_name= short_name, revision = revision)
        odb_file = oda.odb_file
        vma = int(request.query_params.get('addr'))
        try:
            decompiler = OdaDecompiler(odb_file)
            results = decompiler.decompile(vma)

            return Response({
                'start': results.start,
                'end': results.end,
                'source': results.source,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShareView(APIView):
    permission_classes = (HasOdaMasterPermission,)

    def post(self, request):
        short_name = request.data.get('short_name')
        revision = request.data.get('revision')
        oda = OdaMaster.objects.get(short_name=short_name, revision=revision)
        share = Share(odaMaster=oda, name=id_generator(16))
        share.save()
        return Response({
            'shareName': share.name,
            'shareUrl': reverse('connect', args=(share.name,))
        })


class DisassemblerViewSet(viewsets.GenericViewSet):
    @detail_route()
    def architectures(self, request, pk):
        return Response({
            'architectures': get_supported_archs(),
            'endians': [{
                'name': x,
                'intValue': y
            } for x, y in get_supported_endians().items()]
        })

    @detail_route()
    def options(self, request, pk):
        arch = request.query_params.get('arch', 'i386:x86-64')
        return Response({
            'arch': arch,
            'options': get_platform_options2(arch)
        })
