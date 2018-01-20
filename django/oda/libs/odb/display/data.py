import string
import html
from binascii import hexlify

from oda.libs.odb.display.base import DisplayGenerator, DisplayUnit
from oda.libs.odb.structures.defined_data import DefinedData, DefinedDataList
from oda.libs.odb.structures.c_struct import CStruct, CStructList, BuiltinField
from oda.libs.odb.structures.types import BuiltinType, BuiltinTypeFactory

class DataDisplayGenerator(DisplayGenerator):

    def __init__(self, context):
        super().__init__(context)
        self.defined_data = DefinedDataList(
                                self.context.odb_file.get_structure_list(
                                    DefinedData))

    def display(self):

        dataLen = self.context.cur_end - self.context.cur_start
        numLines = 0
        sec_name = self.context.section.name

        # Get the raw data from the file
        rawData = self.context.ofd.bfd.raw_data(
                        self.context.ofd.bfd.sections[sec_name],
                        self.context.cur_start, dataLen)

        addr = self.context.cur_start
        byteList = list(rawData)
        while len(byteList) and numLines < self.context.maxLines:

            # if we have defined data at this address
            dd = self.defined_data.find_by_vma(addr)
            if dd is not None:
                # parse the defined data type
                numLines += self.displayDefinedData(addr, dd, byteList)
                addr += dd.size
            # else, the data is undefined, so treat it as single byte per line
            else:
                # TODO: Don't specify the css class here - it's not very classy, ha, ha
                c = byteList.pop(0)
                du = DisplayUnit()
                du.isCode = False
                du.vma = addr
                du.section_name = sec_name
                du.instStr = "<insn>db</insn>  <span class='raw'>%02xh</span>" % c
                if chr(c) in string.printable:
                    du.instStr += " <span class='comment'>; %s</span>" % html.escape(chr(c))
                du.rawBytes =  '%02x' % c
                du.isArray = False
                du.dataSize = 1
                addr += 1
                numLines += 1
                self.context.displayUnits[du.vma] = du

        return numLines


    def displayDefinedData(self, addr, dd, byteList):
        if dd.type_kind == CStruct.kind:
            return self.displayStruct(addr, dd.type_name, dd.var_name, byteList)
        elif dd.type_kind == BuiltinType.kind:
            return self.displayPrimitive(addr, dd, byteList)

    def displayPrimitive(self, addr, dd, byteList):

        MAX_RAW_BYTES_DISPLAY = 6
        builtin = BuiltinTypeFactory(dd.type_name)

        barray = bytearray(byteList[0:dd.size])
        del byteList[:dd.size]

        fmt = builtin.format(barray)
        du = DisplayUnit()
        du.instStr = "<insn>%s</insn>  <span class='raw'>%s</span>" % (dd.var_name,
                                                                       fmt)
        hexBytes = hexlify(barray[0:MAX_RAW_BYTES_DISPLAY]).decode('ascii')
        if len(barray) > MAX_RAW_BYTES_DISPLAY:
            hexBytes += "..."

        du.rawBytes = hexBytes
        du.isArray = False
        du.dataSize = dd.size
        du.vma = addr
        du.section_name = self.context.section.name
        self.context.displayUnits[du.vma] = du

        return 1

    def displayStruct(self, addr, struct_name, var_name, byteList):

        cstructList = CStructList(self.context.odb_file.get_structure_list(CStruct))
        struct = cstructList.find_by_name(struct_name)
        numLines = len(self.context.displayUnits)
        newLines = 0
        for field in struct.fields:
            if field.size > 0:
                if isinstance(field, BuiltinField):
                    self.displayField(addr, field, var_name, byteList)
                else:
                    self.displayStruct(addr, field.cstruct, var_name + '.' + field.name,
                                byteList)
                addr += field.size
                newLines += 1
                if numLines+newLines == self.context.maxLines:
                    break

        return newLines

    def displayField(self, addr, field, prefix, byteList):

        valueStr = '0x'
        rawBytes = ''
        for i in range(field.size):
            c = byteList.pop(0)
            valueStr += "%02x" % c
            rawBytes += "%02x" % c
        du = DisplayUnit()
        insn = prefix + '.' + field.name
        du.instStr = "<insn>%s</insn>  <span class='raw'>%s</span>" % (insn, valueStr)
        du.rawBytes = rawBytes
        du.isArray = False
        du.dataSize = field.size
        du.vma = addr
        du.section_name = self.context.section.name
        self.context.displayUnits[du.vma] = du

