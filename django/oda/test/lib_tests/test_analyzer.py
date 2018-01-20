import os
from oda.libs.odb.binaries import BinaryFile

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.disassembler.disassembler import Disassembler
from oda.test.oda_test_case import OdaLibTestCase

class TestAnalyzer(OdaLibTestCase):

    def test_total_lines(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())

        dasm = Disassembler(odb_file)
        total_lines = dasm.total_lines()

        self.assertEquals(41614, total_lines)

    def test_analyzer_output(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        dasm = Disassembler(odb_file)

        # Disassemble at a provided vma
        units = dasm.display(0x4095e0, 200, False)

        # The provided address should be the first instruction
        self.assertEquals(0x4095e0, units[0].vma)
        self.assertEquals("mov", units[0].opcode)

        # Another random instruction
        self.assertEquals("test", units[18].opcode)
        self.assertEquals("al,al", units[18].operands)

        # Disassemble at a provided negative vma
        units = dasm.display(0x4095e0, -10, False)

        # The provided address should be the last instruction
        self.assertEquals(0x4095e0, units[9].vma)
        self.assertEquals("mov", units[9].opcode)
        # IDA finds this one through a function pointer in data section
        # self.assertEquals(True, units[9].isFunction)

        # 9 instructions earlier
        self.assertEquals(0x4095BB, units[0].vma)
        self.assertEquals("call", units[0].opcode)

        # Disassemble a function
        units = dasm.display(0x40BEE0, 10, False)
        self.assertEquals(True, units[0].isFunction)

        # Cross Parcel Boundaries
        units = dasm.display(0x412BF4, -10, False)
        self.assertEquals(0x412BF4, units[9].vma)
        self.assertEquals("ret", units[9].opcode)
        self.assertEquals(".fini", units[9].section_name)
        self.assertEquals(0x412BE1, units[2].vma)
        self.assertEquals("jmp", units[2].opcode)
        self.assertEquals(".text", units[2].section_name)

        # Cross Code/Data Boundaries
        units = dasm.display(0x412BF4, 10, False)
        self.assertEquals(0x412BF4, units[0].vma)
        self.assertEquals(0x412C00, units[1].vma)
        self.assertEquals(1, units[1].dataSize)




