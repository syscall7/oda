import os
import re
import subprocess

from django.core.management.base import BaseCommand

import oda
from oda.apps.odaweb.examples import Examples
from oda.apps.odaweb.models import OdaMaster, InstDoc, SandboxServer
from oda.apps.odaweb.models.oda_master import OdaMasterPermissionLevel
from oda.libs.odb import structures
from oda.libs.odb.binaries import BinaryString, BinaryFile
from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.ops.comment_operations import CreateCommentOperation
from oda.libs.odb.ops.label_operations import CreateLabelOperation
from oda.libs.odb.structures.label import Label


def load_examples(owner=None):
    EXAMPLES_DIR = os.path.join(os.path.dirname(oda.apps.odaweb.examples.__file__), 'examples')

    for example in Examples:
        short_name = example['short_name']
        valid_file_storage_id = True

        if OdaMaster.objects.filter(short_name=short_name).exists():
            print('Example %s already exists in the database' % short_name)
            oda_master = OdaMaster.objects.filter(short_name=short_name).first()
        else:
            oda_master = OdaMaster(short_name=short_name,
                               project_name=example['project_name'],
                               owner=owner,
                               default_permission=
                               OdaMasterPermissionLevel.read.value)

        print('Adding example %s to database' % short_name)

        if 'data' in example:
            example_data = ''.join(example['data'].split())
            odb_file = OdbFile(BinaryString(example_data, example['options']['architecture']))
        elif 'file_name' in example:
            odb_file = OdbFile(BinaryFile(
                os.path.join(EXAMPLES_DIR, example['file_name']),
                example['options']['target'],
                example['options']['architecture']))

        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        if 'comments' in example:
            for vma, msg in example['comments']:
                odb_file.execute(CreateCommentOperation(vma, msg))
                print("Adding Comment %s To %s" % (msg, str(odb_file)))

        if 'labels' in example:
            for vma, label in example['labels']:
                odb_file.execute(CreateLabelOperation(vma, label))
                print("Saving label %s To %s" % (label, str(odb_file)))


        oda_master.odb_file = odb_file
        oda_master.save()

class TmpSubCode:
    def __init__(self, mnemonic, short):
        self.mnemonic = mnemonic
        self.short = short

    def update_short(self, more_short):
        if self.short.endswith('-'):
            self.short += more_short
        else:
            self.short += ' ' + more_short

            # print 'New short is "%s"' % self.short

    mnemonic = property()
    short = property()

class TmpInstDoc:
    def __init__(self, page_num):
        self.mnemonic = 'unknown'
        self.short = 'uninitialized'
        self.long = ''
        self.page_start = page_num
        self.num_pages = 1
        self.sub_codes = []

        # used in stream filtering of long help
        self.prev_line = ''
        self.page_num_pattern = re.compile('^\s*[0-9]+-[0-9]+ Vol\..*$')

    def update_long(self, line):

        if self.page_num_pattern.match(line):
            return

        if line.strip() == '':
            return

        if line.startswith('\x0c'):
            return

        if self.mnemonic in line and self.short in line:
            return

        line = line.strip()

        if line[0].isupper() and (self.prev_line.endswith('.') or self.prev_line.endswith('.)')):
            self.long += '\n'

        self.prev_line = line
        self.long += self.prev_line + '\n'

    def gen_png(self, directory, name):

        try:
            os.makedirs(directory)
        except OSError:
            pass

        subprocess.check_call('pdftoppm -png -f %d -l %d intel_ref.pdf %s' % (
            self.page_start, self.page_start + self.num_pages - 1, os.path.join(directory, name)), shell=True)

    def gen_pdf(self, directory, name):
        try:
            os.makedirs(directory)
        except OSError:
            pass

        subprocess.check_call('pdftk intel_ref.pdf cat %d-%d output %s.pdf' % (
            self.page_start, self.page_start + self.num_pages - 1, os.path.join(directory, name)), shell=True)

    mnemonic = property()
    short = property()
    long = property()

# Standalone executable to scrape Intel instruction ref
#
# Expects the Intel instruction reference in text form to be in the current
# directory.  The text form of the PDF can be generated with the following
# command:
#
#     pdftotext -layout -enc Latin1 intel_ref.pdf intel_ref.txt
#
# The pdftotext utility is distributed with xpdf.
def load_instdocs():
    # read in text file and extract pages
    with open(os.path.join(os.path.dirname(__file__), 'intel_ref.latin'), 'r') as f:
        txt = f.read()
        pages = txt.split('\f')

    # states
    STATE_FIND_START = 1
    STATE_FIND_SUBCODES = 2
    STATE_FIND_DESC = 3
    STATE_GATHER_DESC = 4

    state = STATE_FIND_START

    inst_docs = []
    desc_start = re.compile(r'^\s*Description.*$')
    desc_end = re.compile(r'^\s*Operation.*$')
    inst_ref = re.compile(r'^\s*INSTRUCTION SET REFERENCE.*$')
    inst_start = re.compile(r'^(?P<mnemonic>[A-Z]+[a-zA-Z/0-9 ]*)\s*-+\s*(?P<short>.*)$')
    sub_code = re.compile(r'(?:[0-9A-F]{2} )+')

    for (page_num, page) in enumerate(pages):

        lines = page.split('\n')

        if state == STATE_FIND_START:
            if inst_ref.match(lines[0]):

                # we already know what the first line of each page looks like, so skip it
                for i in range(1, len(lines)):

                    line = lines[i]
                    inst_match = inst_start.match(line)

                    # ignore empty lines
                    if line == '':
                        continue
                    # NOTE: The only exception when 'Opcode' did not appear within the next
                    #       two lines was for 'MOVS/MOVSB/MOVSW/MOVSD/MOVSQ', which I manually
                    #       fixed up by deleting some empty lines in the input file.
                    elif inst_match and 'Opcode' in '\n'.join(lines[i + 1:i + 2]):
                        cur_inst = TmpInstDoc(page_num + 1)
                        cur_inst.mnemonic = inst_match.group('mnemonic')
                        cur_inst.short = inst_match.group('short')
                        inst_docs.append(cur_inst)
                        state = STATE_FIND_SUBCODES
                    else:
                        break

        # ignore the rest of the page if we're still seeking
        if state != STATE_FIND_START:

            cur_inst.num_pages += 1

            for i in range(1, len(lines)):
                line = lines[i]

                if state == STATE_FIND_SUBCODES:
                    if cur_inst.mnemonic != 'Jcc':
                        state = STATE_FIND_DESC
                    else:
                        desc_match = desc_start.match(line)
                        if desc_match:
                            state = STATE_GATHER_DESC
                            continue

                        # split fields based on 2 or more spaces as the delimiter
                        fields = re.split(r'\s{2,}', line)

                        if len(fields) == 6 and sub_code.match(line):
                            mnemonic = fields[1].split()[0]
                            short = fields[5].strip()
                            cur_inst.sub_codes.append(TmpSubCode(mnemonic, short))
                        # catch any part of the description that wrapped to the next line
                        elif (len(fields) == 2) and fields[0] == '' and lines[i - 1].strip() != '':
                            print(fields[1])
                            # add the text to the last sub code added
                            cur_inst.sub_codes[-1].update_short(fields[1])

                if state == STATE_FIND_DESC:
                    desc_match = desc_start.match(line)
                    if desc_match:
                        state = STATE_GATHER_DESC
                        continue
                elif state == STATE_GATHER_DESC:
                    if desc_end.match(line):
                        state = STATE_FIND_START
                        break
                    else:
                        cur_inst.update_long(line)

    for (i, inst) in enumerate(inst_docs):

        # split mnemonic_a/mnemonic_b/mnemonic_c apart
        for mnemonic in inst.mnemonic.split('/'):

            if InstDoc.objects.filter(mnemonic=mnemonic).exists():
                print('Instruction %s already exists in the database' % mnemonic)
                continue

            print('Adding instruction %s' % mnemonic)
            inst_doc = InstDoc(
                platform='i386',
                mnemonic=mnemonic,
                short=inst.short.decode('latin-1').encode('utf-8'),
                long=inst.long.decode('latin-1').encode('utf-8'))

            inst_doc.save()

        # process sub-instructions (i.e., JNE is a "sub" instruction of Jxx)
        for sub in inst.sub_codes:

            if InstDoc.objects.filter(mnemonic=sub.mnemonic).exists():
                print('Sub instruction %s already exists in the database' % sub.mnemonic)
                continue

            print('Adding sub instruction %s: %s' % (sub.mnemonic, sub.short))
            inst_doc = InstDoc(
                platform='i386',
                mnemonic=sub.mnemonic,
                short=sub.short.decode('latin-1').encode('utf-8'),
                long=inst.long.decode('latin-1').encode('utf-8'))

            inst_doc.save()


def load_sandbox_servers():
    server = SandboxServer(ip='localhost', port=8090)
    server.save()


class Command(BaseCommand):
    args = '<>'
    help = 'Setup ODA'

    def handle(self, *args, **options):
        load_examples()

        # TODO: I'm commenting this out for now until we add support back in the client
        # load_instdocs()

        load_sandbox_servers()
        print('\nODA setup was successful!')
