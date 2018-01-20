import logging
import string

import bfd
from oda.libs.odb.disassembler.ofd import Ofd
from oda.libs.odb.display.parcel import ParcelDisplayGenerator
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.defined_data import DefinedDataList, DefinedData

logger = logging.getLogger(__name__)


class DisplayContext(object):
    """ This class holds the information needed to generate display units. """

    def __init__(self, odb_file, vma_start, vma_end, maxLines,
                 analyzer):

        self.odb_file = odb_file
        self.ofd = Ofd(odb_file.get_binary())

        # represents the start and end address that we are displaying
        self.vma_start = vma_start
        self.vma_end = vma_end

        # moving window that we are currently processing (initialized to
        # entire range to start)
        self.cur_start = vma_start
        self.cur_end = vma_end

        self.displayUnits = {}
        self.maxLines = maxLines
        self.analyzer = analyzer
        self.functions = {}
        self.labels = []

        # Grab some data structures for convenience and performance reasons
        self.symbols = self.odb_file.get_structure_list(Symbol)
        self.defined_data = DefinedDataList(
            self.odb_file.get_structure_list(DefinedData))

        self.options = self.analyzer.processOptions(
            self.odb_file.get_binary().options.get_extra_options())

        # Add symbols from the database to the functions list
        for f in self.odb_file.get_structure_list(Function):
            self.functions[f.vma] = f

    @property
    def section(self):
        return self.ofd.get_section_from_addr(self.cur_start)

class DisplayMaster(object):

    def __init__(self, odb_file, analyzer):
        self.analyzer = analyzer
        self.odb_file = odb_file

    def display(self, parcels, start=0, maxUnits=None):

        # make sure parcels are in order
        parcels.sort(key=lambda p: p.vma_start, reverse=False)

        # Filter parcels based on the provided boundaries
        if maxUnits >= 0 or maxUnits == None:
            # Getting disassembly greater than an address
            filterFunc = lambda parcel: parcel.vma_end >= start
            parcelList = parcels

            # Forwards parsing starts at a given address until we get enough units
            disEnd = None
            disStart = start

        else:
            # Note: disassembler.py prevents this case from happening.
            # TODO: To remove

            # Getting disassembly moving backwards from an address
            #  Note: Use start+1 to include the provided address in the returned disaseembly
            filterFunc = lambda parcel: parcel.vma_start < start + 1
            parcelList = reversed(parcels)

            # Backwards parsing means the provided start address is the end of disassembly
            disEnd = start + 1
            disStart = None
            maxUnits = abs(maxUnits)

        context = DisplayContext(self.odb_file, disStart, disEnd, maxUnits,
                                 self.analyzer)

        # Disassemble the parcel(s)
        pd = ParcelDisplayGenerator(context)
        for parcel in filter(filterFunc, parcelList):

            # display the next parcel
            pd.display(parcel)

            # Breakout early if we parse enough units
            if context.maxLines is not None:
                context.maxLines = maxUnits - len(context.displayUnits.keys())
                if context.maxLines <= 0:
                    break

        logger.debug("Display master completed.")

        return context.displayUnits

    def get_text_listing(self, parcels):

        parcels.sort()
        MAX_SEC_NAME_WIDTH = 32
        ofd = Ofd(self.odb_file.get_binary())

        def funcFmtCode(addr, rawData, instr, abfd, sec_name):
            ret = ''
            if addr in abfd.syms_by_addr:
                ret += '\n%s:%08x <%s>:\n' % (sec_name, addr, abfd.syms_by_addr[addr].name)
            if abfd.bpc > 1 and abfd.endian is bfd.ENDIAN_LITTLE:
                bytes = ''.join(['%02x ' % i for i in reversed(rawData)])
            else:
                bytes = ''.join(['%02x ' % i for i in rawData])

            ret += '%s:%08x %-32s %s\n' % (sec_name.rjust(MAX_SEC_NAME_WIDTH, ' '), addr, bytes, instr)
            return ret

        # TODO: refactor and use parseDataParcel
        def fmtDataParcel(p):
            ret = ''
            # Get the raw data from the file
            rawData = ofd.bfd.raw_data(ofd.bfd.sections[p.sec_name], p.vma_start, p.vma_end - p.vma_start)
            i = 0
            for b in rawData:
                ret += '%s:%08x %-32s %s %s\n' % (p.sec_name.rjust(MAX_SEC_NAME_WIDTH, ' '),
                                                  p.vma_start+i,
                                                  '%02x' % ord(b),
                                                  '0x%02x' % ord(b),
                                                  '\'%s\'' % b if b in string.printable else '')
                i += 1
            return ret

        options = self.analyzer.processOptions(
                    self.odb_file.get_binary().options.get_extra_options())
        listing = ''
        for p in parcels:
            if p.is_code:
                (output, _, _) = ofd.disassemble(p.sec_name,
                                                 options=options,
                                                 start=p.vma_start,
                                                 stop=p.vma_end,
                                                 funcFmtLine=funcFmtCode,
                                                 funcFmtLineArgs={
                                                     'sec_name': p.sec_name
                                                 })
            else:
                output = fmtDataParcel(p)

            listing += output

        return listing


