from abc import ABC, abstractmethod
from oda.libs.odb.disassembler.processors.instruction import InstructionType, callType

class DisplayUnit(object):

    def __init__(self):
        self.section_name = ""
        self.vma = 0
        self.rawBytes = ""
        self.instStr = ""
        self.branch = ""
        self.branch_label = ""
        self.isFunction= False
        self.isBranch= False
        self.branchRef = None
        self.stringRef = None
        self.targetRef = None
        self.crossRef = []
        self.opcode = ''
        self.operands = ''
        self.isError = False
        self.isTargetAddrValid = False
        self.instType = InstructionType.undefined
        self.callType = None
        self.targetAddr = 0
        self.labelName = 'abc'
        self.isCode = True
        self.size = 0


class DisplayGenerator(ABC):
    """ This is an abstract class to be inherited by classes that generate
    display units given a DisplayContext."""

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def display(self):
        """ Generate/modify display units in the current context """
