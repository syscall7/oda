import bfd
import logging

logger = logging.getLogger(__name__)

TARGETS_WITHOUT_CODE_SECTIONS = ['binary', 'ihex', 'srec']
UNKNOWN_ARCH = 'UNKNOWN!'

class SectionInfo(object):
    def __init__(self, sections):
        self.sections = sections
        if len(sections):
            self.start_addr = sections[0].vma
            self.stop_addr = sections[-1].vma + sections[-1].size - 1
        else:
            self.start_addr = 0
            self.stop_addr = 0

    addr_range = property(lambda self: self.stop_addr - self.start_addr)

class Ofd(object):
    ''' ODA File Descriptor (wrapper for BFD) '''

    def __init__(self, binary):

        self.binary = binary

        self.bfd_file_handle = binary.file_handle()
        filename = self.bfd_file_handle.name

        # we manually fixup the section start address if a base address is set
        baseAddr = self.binary.options.base_address
        if baseAddr:
            baseAddr = int(baseAddr, 16)
        else:
            baseAddr = 0

        # internal BFD object
        assert(binary.options.architecture != UNKNOWN_ARCH)
        self.bfd = bfd.Bfd(filename, binary.options.target, binary.options.architecture)

        self.sections = sorted(list(self.bfd.sections.values()), key=lambda s: s.vma)
        for s in self.sections:
            # manually add in the base address, so the parcels know their real vma
            s.vma += baseAddr

            # iterate over the flags and convert them to boolean attributes
            for f in bfd.FLAGS:
                if f.name in s.flags:
                    setattr(self, f.name, True) # i.e, section.SEC_ALLOC = True
                else:
                    setattr(self, f.name, False) # i.e, section.SEC_ALLOC = False

    def __del__(self):
        if hasattr(self, 'disassembler'):
            self.bfd.close()
            self.bfd_file_handle.close()
            try:
                self.bfd_file_handle.done()
            except AttributeError:
                #Doesn't have done, maybe doesn't need it?
                pass

    def sectionFlagsInfo(self):
        return bfd.FLAGS

    def sections_iter(self, flags=[]):
        '''Iterate over all sections (in ascending address order) that have all give flags specified'''
        for sec in self.sections:
            sec_flags = [f.name for f in sec.flags]
            if set(flags).issubset(sec_flags):
                yield sec

    def section_has_flags(self, section, flags=[]):
        sec_flags = [f.name for f in section.flags]
        if set(flags).issubset(sec_flags):
            return True
        else:
            return False

    def is_valid_code(self, vma):
        return False

    def disassemble(self, name, options=[], start=None, stop=None, numLines=None, funcFmtLine=None, funcFmtLineArgs=None):
        sec = self.bfd.sections[name]

        # We no longer have need for the baseAddr arg here, because we manually fixup the section addresses in the
        # constructor above.  This change was precipitated by the fact that the parcels need to know their vma, and the
        # the push_vma in the Parcel scanner was adding a vma that had the base address added twice.
        baseAddr = None

        # determine endianness
        endian = ({'BIG': bfd.ENDIAN_BIG,
                    'LITTLE': bfd.ENDIAN_LITTLE,
                    'DEFAULT': bfd.ENDIAN_DEFAULT})[self.binary.options.get_endian()]

        # force intel syntax as default for i386 arch
        if self.bfd.arch.startswith('i386') and len(options) == 0:
            options.append('intel-mnemonic')

        options_string = ",".join(options)

        dis = self.bfd.disassemble(sec, start, stop, numLines, None, funcFmtLine, funcFmtLineArgs, endian, options_string, baseAddr)
        return dis

    def symbol(self, lookup):
        '''Lookup can either be address or name'''
        if type(lookup) == int:
            return bfd.syms_by_addr[lookup]
        elif type(lookup) == str:
            return bfd.syms_by_name[lookup]
        else:
            raise Exception('Can\'t lookup symbol by type %s' % type(lookup))

    def symbols(self):
        '''Returns a list of Symbols sorted by increasing address'''
        # syms = [sym for (name, sym) in sorted(self.disassembler.syms_by_name.iteritems(), key=lambda (name, sym): sym.value)]
        syms = sorted([sym for (name, sym) in self.bfd.syms_by_name.items()], key=lambda sym: sym.value)
        return syms

    def is_code_section(self, sec):
        return self.section_has_flags(sec, ['SEC_CODE'])

    def get_code_sections(self):

        def filter_sec_code(sec):
            return set(['SEC_CODE']).issubset([f.name for f in sec.flags])

        code_sections = filter(filter_sec_code, self.sections)

        section_info = SectionInfo(code_sections)

        return section_info

    def get_loadable_sections(self):

        def filter_sec_load(sec):
            return set(['SEC_LOAD']).issubset([f.name for f in sec.flags])

        # treat all sections as loaded for targets without code sections
        if self.bfd.target in TARGETS_WITHOUT_CODE_SECTIONS:
            loadable_sections = self.sections
        # else, only get the code sections
        else:
            loadable_sections = list(filter(filter_sec_load, self.sections))

        section_info = SectionInfo(loadable_sections)

        return section_info

    def get_section_from_addr(self, addr):
        for sec in self.sections:
            if addr >= sec.vma and addr < (sec.vma+sec.size):
                return sec

        return None


