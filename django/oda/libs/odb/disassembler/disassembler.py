import re
import bfd
from functools import reduce

import oda.libs.odb.disassembler.processors.processor
from oda.libs.odb.disassembler.processors.processor import get_processor
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.ops.create_function_operation import CreateFunctionOperation, EditFunctionOperation, DeleteFunctionOperation
from .ofd import UNKNOWN_ARCH

from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.label import Label

from oda.libs.odb.display.master import DisplayMaster

def get_supported_archs():
    '''Return a list of all architectures supported
    '''
    supportedArchs = bfd.list_architectures()

    # Remove Problem archs
    problemArchs = ['MicroBlaze',
                    'i960:ka_sa',
                    'i960:kb_sb',
                    'r800',
                    'moxie',
    ]

    for arch in problemArchs:
        if arch in supportedArchs:
            supportedArchs.remove(arch)

    return supportedArchs


def get_supported_endians():
    endians = {
        'DEFAULT': bfd.ENDIAN_DEFAULT,
        'LITTLE': bfd.ENDIAN_LITTLE,
        'BIG': bfd.ENDIAN_BIG
    }

    return endians

def get_platform_options(platform):
    djhtmlOpts = []
    analyzer = get_processor(platform, None)
    if analyzer == None:
        analyzer = get_processor('defaultAnalyzer', None)

    #print "Checking if"
    if analyzer.options:
        #print "ANalyzer",analyzer.options
        for opt in analyzer.options:
        # Form the name of the widget by stripping out options
            widgetName = opt[0].replace(' ', '')
            widgetType = ''
            if opt[2] == 'CHOICE' or opt[2] == 'BOOL':
                widgetType = 'select'
                widgetName += widgetType

            # Build the Modal
            djhtmlOpts.append((widgetName,widgetType) + opt)
            #print 'DHTML',djhtmlOpts
    return djhtmlOpts

def get_platform_options2(platform):
    analyzer = get_processor(platform, None)
    if analyzer == None:
        analyzer = get_processor('defaultAnalyzer', None)

    return [{
        'name': x[0],
        'desc': x[1],
        'type': x[2],
        'values': x[3]
    } for x in analyzer.options]

class Disassembler(object):
    def __init__(self, odb_file):
        self.odb_file = odb_file
        architecture = self.odb_file.get_binary().options.architecture
        self.analyzer = get_processor(architecture, odb_file)

    def total_lines(self):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return parcels.sum_ldas()

    def vma_to_lda(self, vma):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return parcels.vma_to_lda(vma)

    def lda_to_vma(self, lda):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return parcels.lda_to_vma(lda)

    def make_data(self, vma):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(vma)
        if not p.is_code:
            raise Exception("Cannot make data on non-code parcel")
        self.odb_file.execute(SplitParcelOperation(vma))

    def make_code(self, vma):
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        p = parcels.find_parcel_by_vma(vma)
        if p.is_code:
            raise Exception("Cannot make code on a code parcel")
        self.odb_file.execute(ActiveScanOperation(vma))

    def make_function(self, vma, name, args, retval):
        self.odb_file.execute(CreateFunctionOperation(vma, name, args, retval))

    def edit_function(self, vma, name, args, retval):
        self.odb_file.execute(EditFunctionOperation(vma, name, args, retval))

    def delete_function(self, vma):
        self.odb_file.execute(DeleteFunctionOperation(vma))

    def display(self, start, lines, logical):

        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))

        # if we are analyzing based on lda, first convert to vma
        if logical:
            start = parcels.lda_to_vma(start)
            if start is None:
                # TODO: Throw exception here?
                return []

        # if we are going backwards
        if lines < 0:
            # Note: Use start+1 to include start in the returned disassembly
            lda_end = parcels.vma_to_lda(start) + 1
            lda_start = lda_end + lines if lda_end > lines else 0
            start = parcels.lda_to_vma(lda_start)
            lines = abs(lines)

        parcels = [p for p in parcels if p.vma_end > start and p.size > 0]

        display = DisplayMaster(self.odb_file, self.analyzer)
        dus = display.display(parcels, start, lines)

        sorted_du = list(dus.values())
        sorted_du.sort(key=lambda x: x.vma, reverse=False)
        return sorted_du

    def unused_get_text_listing_via_dus(self):
        dus = self.display(0, self.total_lines(), True)
        functions = {f.vma: f for f in self.odb_file.get_structure_list(Function)}
        labels = {l.vma:l.label for l in self.odb_file.get_structure_list(Label)}
        listing = ''
        # calculate the maximum width needed to fit the longest raw bytes
        max_raw_width = reduce(lambda x, y: x if x > len(y.rawBytes) else len(y.rawBytes), dus, 0)
        max_sec_width = reduce(lambda x, y: x if x > len(y.section_name) else len(y.section_name), dus, 0)
        for du in dus:

            if du.vma in functions.keys():
                listing += '%s            %s ; ======================== FUNCTION =========================\n' % (' '*max_sec_width, ' '*max_raw_width)
                listing += '%s            %s %s\n' %  (' '*max_sec_width, ' '*max_raw_width, functions[du.vma].name)
            if du.vma in labels.keys():
                listing += '%s:0x%08x      %s:\n' % (du.section_name.rjust(max_sec_width, ' '),
                                                  du.vma,
                                                  labels[du.vma])
            target = ''
            if du.isTargetAddrValid:
                target = labels[du.targetAddr] if du.targetAddr in labels.keys() else '0x%08x' % du.targetAddr

            listing += '%s:0x%08x %s %s %s\n' % (du.section_name.rjust(max_sec_width, ' '),
                                              du.vma,
                                              du.rawBytes.ljust(max_raw_width, ' '),
                                              du.instStr,
                                              target)
        return listing

    def get_text_listing(self):
        display = DisplayMaster(self.odb_file, self.analyzer)
        parcels = ParcelList(self.odb_file.get_structure_list(Parcel))
        return display.get_text_listing(parcels)


    @staticmethod
    def guess_bfd_arch(filename):
        ''' Returns our best guess at target (file format) and architecture '''

        # use defaults these default when we can't detect the arch/target
        arch = UNKNOWN_ARCH
        target = 'binary'
        try:
            target_archs = bfd.guess_target_arch(filename)

            # TODO: Present these options to the user and let them pick from all matching target/archs

            # for each detected target/arch
            for (t, a) in target_archs:

                # we'll set the target here even in cases where we cannot detect arch (i.e., ihex, srec)
                target = t
                if a != "UNKNOWN!":
                    arch = a
                    break

        except bfd.BfdFileFormatException as e:
            pass
        except Exception as e:
            pass

        return arch, target

    def find(self, pattern):

        # NOTE: This function is obnoxiously complex because we want to find sequences of bytes that span contiguous
        #       sections

        # dictionary of results with key=address value=section_name
        results = {}

        # current contiguous chunk of bytes to search within
        haystack = ''

        # last address of the chunk of bytes in haystack
        lastAddr = -1

        # first address of the chunk of bytes in haystack
        baseAddr = -1

        # sections making up haystack
        sectionGroup = []

        # make sense of the user's search pattern
        def parsePattern(pattern):
            import binascii
            if pattern.startswith('"') and pattern.endswith('"'):
                return pattern[1:-1]
            else:
                try:
                    return binascii.unhexlify(pattern.replace(' ', ''))
                except TypeError:
                    # Assume this is a string to search for
                    # TODO: Throw the error and color a text box in the UI
                    return pattern
        # find the pattern in the current haystack
        def needleInHaystack(needle, haystack, baseAddr, sectionGroup, results):

            haystack = haystack.decode('latin1')
            if type(needle) is bytes:
                needle = needle.decode()

            for m in re.finditer("(%s)" % re.escape(needle), haystack):

                foundAddr = baseAddr+m.start()

                for s in sectionGroup:
                    if foundAddr >= s.vma and foundAddr < s.vma+s.size:
                        results[foundAddr] = s.name
                        break;

        pattern = parsePattern(pattern)

        # we only search within loadable sections
        for s in self.analyzer.ofd.get_loadable_sections().sections:

            # if this section is contiguous with the previous section
            if s.vma == lastAddr:
                haystack += self.analyzer.ofd.bfd.raw_data(s, s.vma, s.size)
                sectionGroup.append(s)
                lastAddr = s.vma+s.size

            # else, this section is not contiguous
            else:
                if lastAddr != -1:
                    needleInHaystack(pattern, haystack, baseAddr, sectionGroup, results)

                # start fresh
                haystack = self.analyzer.ofd.bfd.raw_data(s, s.vma, s.size)
                baseAddr = s.vma
                lastAddr = s.vma+s.size
                sectionGroup = [s]

        # search the last contiguous group
        if lastAddr != -1:
            needleInHaystack(pattern, haystack, baseAddr, sectionGroup, results)

        return results

