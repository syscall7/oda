import logging
import re

from oda.libs.odb.disassembler.ofd import Ofd
from .instruction import *

logger = logging.getLogger(__name__)

class Processor(object):
    '''
    classdocs
    '''

    def __init__(self, odb_file):

        self.vma = ""
        self.vmaStr = []
        self.branchLineHtml = ""
        self.largestInstSize = 0
        self.opcodeTypes = {}
        self.instSampleInterval = 50

        # {funcAddrA: [crossRef0, crossRef1], funcAddrB: [crossRef0, crossRef1]}
        self.options = []
        # raw binary bytes "xx xx xx .."
        self.rawBytesRegExStr = "((?:[0-9a-f]{2} )+)" 

        self.errorInstRegExStr = "\(bad\)"
        self.errorInstRegEx = re.compile(self.errorInstRegExStr)

        # don't include "<symbol_name>" as part of operands
        self.opcodeRegExStr = "^(\w+)\s+([^<]+)"
        self.opcodeRegEx = re.compile(self.opcodeRegExStr)

        self.odb_file = odb_file

        self.instParserRegEx = re.compile(
            # beginning of the line plus white space
            "^\s*" +
            # vma, followed by white space
            "([0-9a-f]*)\s+" +
            # raw binary bytes
            self.rawBytesRegExStr +
            # instruction
            "\s+(.*)$"
        )

        # in this case, the analyzer is severely crippled and only useful for getting platform options
        if odb_file:
            self.ofd = Ofd(odb_file.get_binary())

    # override this in the subclass if you need to (i.e., mips)
    def processOptions(self, options):
        return options

    def getInstructionType(self,opcode):
        if opcode in self.opcodeTypes:
            return self.opcodeTypes[opcode]
        return InstructionType.normal

    # override in the sub-class
    def computeTargetAddr(self,inst):
        pass

    # override in the sub-class
    def getMaxInstructionLenBytes(self):
        pass


def get_processor(arch, odb_file):
    # for now, ignore everything after the colon
    arch = arch.split(':')[0]
    name = 'oda.libs.odb.disassembler.processors.' + arch
    try:
        mod = __import__(name)
    except ImportError as e:
        return Processor(odb_file)

    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)

    initFunc = getattr(mod, arch)
    obj = initFunc(odb_file)

    return obj