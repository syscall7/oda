import json
import logging
import socket

import dns.resolver
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from lazysignup.decorators import allow_lazy_user

from .examples import Examples
from oda.apps.odaweb.models import OdaMaster, InstDoc, BinaryFile, BinaryFileModel, Share
from oda.apps.odaweb.models.oda_master import odb_file_system, OdaMasterPermissionLevel
from oda.libs.odb.disassembler.disassembler import get_supported_archs, get_supported_endians, get_platform_options, \
    Disassembler
from oda.libs.odb.disassembler.ofd import Ofd
from oda.libs.odb.odb_file import OdbFile

from oda.libs.odb.ops.idb_import_operation import IdbImport

logger = logging.getLogger(__name__)

from .utils import id_generator

EXAMPLE_NAMES = [e['short_name'] for e in Examples]


def render_to_json(context):
    return HttpResponse(json.dumps(context), content_type='application/json')


def password_reset(request, uidb64, token):
    return render(request, 'password_reset_confirm.html', { 'uidb64': uidb64,  'token': token })

def save(request):
    class SaveForm(forms.Form):
        short_name = forms.CharField(required=True)
        revision = forms.CharField(required=True)

    save_form = SaveForm(request.POST)

    if save_form.is_valid():
        request.session['saved'] = True
        u = reverse('index', args=(save_form.cleaned_data['short_name'], save_form.cleaned_data['revision']))

        data = json.dumps({'url': u})

        return HttpResponse(data, content_type='application/json')

    return HttpResponse("Session Not Initialized", status=400)


def create_session(request, to_copy_id, to_copy_version):
    request.session['files'] = []

    if not to_copy_id:
        to_copy_id = 'strcpy_x86'

    if not to_copy_version:
        to_copy_version = 0

    oda_master = OdaMaster.objects.get(short_name=to_copy_id, revision=to_copy_version)
    odb_file = oda_master.odb_file
    oda_master.id = None
    oda_master.short_name = id_generator()
    oda_master.save()
    odb_file_system.store_odb_file(oda_master, odb_file)
    request.session["disassembly_token"] = {
        'id': oda_master.short_name,
        'version': oda_master.revision
    }
    logger.info(
        '%s(%d)' % (request.session["disassembly_token"]['id'], request.session['disassembly_token']['version']))

    return oda_master


def get_session(request):
    try:
        o_id = request.session["disassembly_token"]['id']
        version = request.session["disassembly_token"]['version']

        logger.info("LOADING %s %s", o_id, str(version))
        o = OdaMaster.objects.get(short_name=o_id, revision=version)
        logger.info("FOUND $$$$ " + str(o))
        return o
    except KeyError:
        logger.warn("disassembly_token isn't set")
        return None


def options_form(request):
    # oda_master = get_session(request)
    arch = request.GET['arch']  # oda_master.odb_file.get_binary().options.architecture
    baseAddr = 0  # oda_master.odb_file.get_binary().options.base_address
    selected_opts = []

    class HexUploadForm(forms.Form):
        hex_val = forms.CharField(required=False)
        arch = forms.CharField(required=False)
        base_address = forms.CharField(required=False)
        endian = forms.CharField(required=False)

    return render(request, 'form-platform-options.djhtml', {
        'arch': arch,
        'supported_archs': get_supported_archs(),
        'supported_endians': get_supported_endians(),
        'options': get_platform_options(arch),
        'base_address': baseAddr,
        'selected_opts': selected_opts,
        'form': HexUploadForm(),
        'form_type': 'live'

    })


def fileinfo(request):
    oda_master = get_session(request)
    if not oda_master:
        return HttpResponse("Session Not Initialized", status=400)

    binary = oda_master.binary
    dasm = Disassembler(binary)

    malware = False

    # lookup in malware hash registry
    try:
        [cymru_record, ] = dns.resolver.query('%s.malware.hash.cymru.com' % binary.md5(), 'TXT')
        malware = True
        logger.info('cymru is %s' % cymru_record)
    # if the name does not exist, this binary is not recognized as malware
    except dns.resolver.NXDOMAIN:
        pass
    # Timeout should not ever happen, but sometimes it does
    # TODO: Indicate to the user, that it is unknown
    except dns.resolver.Timeout:
        pass

    # lookup in national software reference library
    benign = False
    try:
        sock = socket.create_connection(('nsrl.kyr.us', 9120), timeout=0.5)
        sock.send('Version: 2.0\n')
        ack_ver = sock.recv(4096)
        sock.send('query %s\n' % binary.md5())
        ack_sum = sock.recv(4096)
        sock.send('BYE\n')
        if ack_ver.startswith('OK') and ack_sum.startswith('OK 1'):
            benign = True
        sock.close()
    except Exception:
        pass

    fileinfo_tab = render_to_string('tab_fileinfo.djhtml', {
        'binary': binary,
        'malware': malware,
        'benign': benign,
        'project_name': oda_master.project_name,
    })

    # Return the new disassembly
    return HttpResponse(json.dumps({
        'fileinfo_tab': fileinfo_tab,
        # 'section_flags' : dasm.sectionFlagsInfo(),
    }), content_type='application/json')


def instdoc(request):
    class InstDocForm(forms.Form):
        mnemonic = forms.CharField()

    form = InstDocForm(request.POST, request.FILES)

    if form.is_valid():
        instdoc_html = 'Help not available'

        mnemonic = form.cleaned_data['mnemonic']
        logger.info('Getting instruction documentation for "%s"' % (mnemonic))

        # TODO: Get the actual platform
        result = InstDoc.objects.filter(platform='i386', mnemonic=mnemonic.upper())
        if result:
            doc = result[0]

            oda_master = get_session(request)
            binary = oda_master.binary

            instdoc_html = render_to_string('inst-doc-content.djhtml', {
                'description': doc.short,
            })

        return HttpResponse(json.dumps({
            'instdoc': instdoc_html,
        }), content_type='application/json')


class UploadFileForm(forms.Form):
    MAX_UPLOAD_SIZE_KB = 256000
    filedata = forms.FileField()
    default_sharing_level = forms.CharField(max_length=64)
    project_name = forms.CharField(max_length=64)

    def clean_filedata(self):
        if self.cleaned_data['filedata'].size > self.MAX_UPLOAD_SIZE_KB * 1024:
            raise forms.ValidationError("File must be less than %d KB!" % self.MAX_UPLOAD_SIZE_KB)

        # always return the cleaned data, whether you have changed it or not
        return self.cleaned_data['filedata']


def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    status = 200
    filename = 'unknown'
    if 'filedata' in request.FILES:
        filename = request.FILES['filedata'].name
    if form.is_valid():

        project_name = form.cleaned_data['project_name']
        default_sharing_level = OdaMasterPermissionLevel[form.cleaned_data['default_sharing_level']]

        filedata = form.cleaned_data['filedata']

        idbImport = IdbImport(filedata)
        if idbImport.is_idb():
            binary_file = BinaryFile.create_from_idb(filedata)
            binary_file.save()
            arch, target = idbImport.guess_arch()
            description = idbImport.describe()
        else:
            binary_file = BinaryFile.create(filedata)
            binary_file.save()
            description = binary_file.desc()
            arch, target = Disassembler.guess_bfd_arch(
                            binary_file.file_handle().name)

        oda_master = OdaMaster(short_name=id_generator(), project_name=project_name,
                               default_permission=default_sharing_level.value,
                               ipAddress=request.META.get('REMOTE_ADDR'))
        if request.user.is_authenticated():
            oda_master.owner = request.user

        oda_master.save()

        request.session["disassembly_id"] = oda_master.short_name
        request.session["disassembly_token"] = {
            'id': oda_master.short_name,
            'version': 0
        }

        binary_file.binary_options.architecture = arch
        binary_file.binary_options.target = target
        binary_file.binary_options.save()

        odb_file = OdbFile(BinaryFileModel(binary_file.id))

        # todo this should not be saved until after user has committed options
        oda_master.odb_file = odb_file

        oda_master.save()

        data = {
            'short_name': oda_master.short_name,
            'revision': oda_master.revision,
            'arch': arch,
            'target': target,
            'file_format': description,
        }
    else:
        status = 413
        data = {
            'error': 'Invalid File "%s", maximum size is %d kb' % (filename, UploadFileForm.MAX_UPLOAD_SIZE_KB)
        }

    return HttpResponse(json.dumps(data), content_type='application/json', status=status)


def download_text_listing(request):
    # /odaweb/_download?short_name=strcpy_x86&revision=0
    short_name = request.GET['short_name']  # oda_master.odb_file.get_binary().options.architecture
    revision = request.GET['revision']

    oda_master = OdaMaster.objects.get(short_name=short_name, revision=revision)

    dasm = Disassembler(oda_master.odb_file)
    text_listing = dasm.get_text_listing()
    if 'HTTP_USER_AGENT' in request.META:
        if 'windows' in request.META['HTTP_USER_AGENT'].lower():
            text_listing = text_listing.replace('\n', '\r\n')
    response = HttpResponse(text_listing, content_type='text')
    response['Content-Disposition'] = 'attachment; filename="%s.txt"' % oda_master.project_name
    return response


def make_copy(oda_master, user):
    user_owns = False
    if user.is_authenticated() and oda_master.owner is not None and oda_master.owner.id == user.id:
        user_owns = True

    # make copy
    oda_master.copy = OdaMaster.objects.get(id=oda_master.id)
    oda_master.id = None

    oda_master.odb_file_storage.id = None
    oda_master.odb_file_storage.save()

    if user_owns:
        max_revision = \
            OdaMaster.objects.filter(short_name=oda_master.short_name).aggregate(max_revision=Max('revision'))[
                'max_revision']
        oda_master.revision = max_revision + 1
    else:
        oda_master.short_name = id_generator()
        oda_master.revision = 0

    oda_master.owner = user
    oda_master.save()

    return oda_master


@login_required
def connect(request, share_name):
    share = Share.objects.get(name=share_name)

    return odb_file_view(request, share.odaMaster)

@allow_lazy_user
def oda(request, short_name):
    import os
    from django.conf import settings
    index_file = os.path.join(settings.BASE_DIR, '..', '..', 'web', 'dist', 'index.html')
    print(index_file)
    html = open(index_file).read()
    return HttpResponse(html)

@allow_lazy_user
def ace(request, short_name, version=0):


    if not short_name:
        short_name = 'strcpy_x86'

    # Sanity check version to avoid web crawler problems
    try:
        int(version)
    except ValueError:
        return HttpResponse("Session Not Initialized", status=400)

    oda_master = OdaMaster.objects.filter(short_name=short_name, revision=version).last()

    if oda_master is None:
        context = {
            'short_name': short_name,
            'revision': version
        }
        return render(request, 'not_found.djhtml', context)

    if oda_master.owner != request.user and oda_master.short_name in EXAMPLE_NAMES:
        oda_master = make_copy(oda_master, request.user)
        return redirect('index_without_revision', short_name=oda_master.short_name)

    return odb_file_view(request, oda_master)

@allow_lazy_user
def oda_master_details(request, short_name, version=0):
    saved = request.session.get('saved', False)
    oda_master = OdaMaster.objects.filter(short_name=short_name, revision=version).last()
    binary = oda_master.odb_file.get_binary()
    section_info = Ofd(oda_master.odb_file.get_binary()).get_loadable_sections()
    context = {
        'isLazyUser': request.user.is_lazy_user(),
        'examples': [{'project_name': x['project_name'], 'short_name': x['short_name']} for x in Examples],
        'master': {
            'project_name': oda_master.project_name,
            'short_name': oda_master.short_name
        },
        'binary': {
            # 'liveMode': binary.is_live_mode()
            'target': binary.options.target,
            'arch': binary.options.architecture,
            'size': binary.size,
            'options': {
                'architecture': binary.options.architecture,
                'base_address': binary.options.base_address,
                'endian': binary.options.endian,
                'selected_opts': binary.options.selected_opts
            }
        },
        'section_info': {
            'start_addr': section_info.start_addr,
            'stop_addr': section_info.stop_addr
        },
        'saved': saved,
        'architectures': get_supported_archs(),
        'endians': [{
            'name': x,
            'intValue': y
        } for x, y in get_supported_endians().items()]
    }
    return render_to_json(context)


def odb_file_view(request, oda_master):
    saved = request.session.get('saved', False)

    context = {
        'isLazyUser': request.user.is_lazy_user(),
        'examples': [{'project_name': x['project_name'], 'short_name': x['short_name']} for x in Examples],
        'master': oda_master,
        'binary': oda_master.odb_file.get_binary(),
        'section_info': Ofd(oda_master.odb_file.get_binary()).get_loadable_sections(),
        'saved': saved,
        'architectures': get_supported_archs(),
        'endians': [{
            'name': x,
            'intValue': y
        } for x, y in get_supported_endians().items()]
    }

    request.session['saved'] = False

    # oda_master = OdaMaster.objects.get(short_name='mkdir', revision=0)
    # odb_file = oda_master.odb_file
    # dasm = Disassembler(odb_file)
    # dunits = dasm.analyze(0, 10000000)
    return render(request, 'ace.djhtml', context)
