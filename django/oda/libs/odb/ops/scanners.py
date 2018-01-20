import logging
import re
import bfd

from oda.libs.odb.disassembler.processors.instruction import InstructionType
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.symbol import Symbol
from abc import ABCMeta, abstractmethod

from oda.libs.odb.display.base import DisplayUnit

logger = logging.getLogger(__name__)

def create_display_unit(analyzer, match_obj, addr, rawData):
    du = DisplayUnit()
    du.vma = addr
    du.opcode = match_obj.group(1)
    du.instType = analyzer.getInstructionType(du.opcode)
    du.operands = match_obj.group(2)
    du.size = len(rawData)

    analyzer.computeTargetAddr(du)

    return du

class HaltScanException(Exception):
    pass

class Scanner(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def scan_line(self, addr, rawData, instr, abfd, parcel):
        pass

    def commit(self, odb_file):
        pass

class ParcelOffsetScanner(Scanner):
    def scan_line(self, addr, rawData, instr, abfd, parcel):
        # associate this vma with the parcel
        parcel.push_vma(addr)

class BranchScanner(Scanner):
    def __init__(self, analyzer):
        self.analyzer = analyzer

        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)
        self.branches = []
        self.labels = []

    def scan_line(self, addr, rawData, instr, abfd, parcel):
        match_obj = self.opcode_regex.match(instr)
        if match_obj:

            du = create_display_unit(self.analyzer, match_obj, addr, rawData)
            if du.instType == InstructionType.branch:
                    self.branches.append({
                        'srcAddr': addr,
                        'targetAddr': du.targetAddr,
                        'instrLen': du.size,
                    })
                # Check if we need to create a label or function

            if du.isTargetAddrValid:

                # Create a new label for branch instructions
                if du.targetAddr not in self.labels and du.instType == InstructionType.branch:
                    self.labels.append(du.targetAddr)

    def commit(self, odb_file):
        for b in self.branches:
            branch = odb_file.create_item(Branch, b)
            odb_file.get_structure_list(Branch).append(branch)

class FunctionScanner(Scanner):

    def __init__(self, analyzer, symbols):

        self.analyzer = analyzer
        self.error_instruction_regex = re.compile(analyzer.errorInstRegExStr)
        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)

        self.functions = {}

        # Create a dictionary of symbols from the symbol table
        self.symbols = {sym.vma: sym for sym in symbols}

    def scan_line(self, addr, rawData, instr, abfd, parcel):
        ''' Disassembly line parser optimized for finding functions '''

        if self.error_instruction_regex.match(instr):
            return

        # Get the Opcode
        match_obj = self.opcode_regex.match(instr)
        if match_obj:
            du = create_display_unit(self.analyzer, match_obj, addr, rawData)

            # If we need to create a function
            if du.isTargetAddrValid and du.instType == InstructionType.call:

                # If this is a new Function
                if du.targetAddr not in self.functions:

                    # Create a generic function name
                    func_name = 'func_%0.8x' % du.targetAddr
                    # If this function exists in the symbol table
                    if du.targetAddr in self.symbols:
                        # Use the function name from the symbol table
                        func_name = self.symbols[du.targetAddr].name

                    self.functions[du.targetAddr] = {
                        'name': func_name,
                        'vma': du.targetAddr,
                        'sym_type': 't',
                        'xrefs':  set([du.vma]),
                        'retval': 'unknown',
                        'args': 'unknown'
                    }
                else:
                    # Else, update a pre-existing Function, add a new cross reference
                    self.functions[du.targetAddr]['xrefs'].update([du.vma])

                # If this is a new Function
                #if du.targetAddr not in self.functions:
                #    self.functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't',
                #                                             set([du.vma]))

                # Else, update a pre-existing Function
                #else:
                 #   # Add new cross reference to set
                  #  self.functions[du.targetAddr].xrefs.update([du.vma])

    def commit(self, odb_file):
        symbols = {sym.vma: sym for sym in odb_file.get_structure_list(Symbol)}
        for addr, f in self.functions.items():
            func = odb_file.create_item(Function, f)
            odb_file.get_structure_list(Function).append(func)

            if addr not in symbols.keys():
                odb_file.insert_item(odb_file.create_item(Symbol, {
                    'name': f['name'],
                    'vma': f['vma'],
                    'base': 0,
                    'sym_type': 't',
                    'value': f['vma'],
                    'xrefs': set([])
                }))


class BadCodeScanner(Scanner):

    def __init__(self, analyzer):

        self.analyzer = analyzer
        self.error_instruction_regex = re.compile(analyzer.errorInstRegExStr)
        self.opcode_regex = re.compile(analyzer.opcodeRegExStr)

        self.functions = {}

        self.bad_addr = None

    def scan_line(self, addr, rawData, instr, abfd, parcel):
        ''' Disassembly line parser optimized for finding functions '''

        if self.error_instruction_regex.match(instr):
            self.bad_addr = addr
            raise bfd.BfdHaltDisassembly("Encountered invalid code")

    """ The following bytes are bad opcodes in x86-64:
               0:   06                      (bad)
               0:   07                      (bad)
               0:   0e                      (bad)
               0:   16                      (bad)
               0:   17                      (bad)
               0:   1e                      (bad)
               0:   1f                      (bad)
               0:   27                      (bad)
               0:   2f                      (bad)
               0:   37                      (bad)
               0:   3f                      (bad)
               0:   60                      (bad)
               0:   61                      (bad)
               0:   9a                      (bad)
               0:   ce                      (bad)
               0:   d4                      (bad)
               0:   d5                      (bad)
               0:   d6                      (bad)
               0:   ea                      (bad)
    """


