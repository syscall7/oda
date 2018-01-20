'''
Created on Jun 12, 2012

@author: Owner
'''
import re
from oda.libs.odb.disassembler.processors.processor import Processor
from oda.libs.odb.disassembler.processors.processor import InstructionType, callType


class i386(Processor):
    '''
    classdocs
    '''

    def __init__(self, odb_file):
        Processor.__init__(self, odb_file)
        
        self.errorInstRegExStr = "\(bad\)"
        self.branchTargetRegEx = re.compile("\w+\s+(0x[0-9a-f]+)")
        self.opcodeTypes = { "jne" : InstructionType.branch,
                             "jo" : InstructionType.branch,
                             "js" : InstructionType.branch,
                               "jns" : InstructionType.branch,
                               "je" : InstructionType.branch,
                               "jz" : InstructionType.branch,
                               "jnz": InstructionType.branch,
                               "jb": InstructionType.branch,
                               "jnae": InstructionType.branch,
                               "jc": InstructionType.branch,
                               "jnb": InstructionType.branch,
                               "jae": InstructionType.branch,
                               "jnc": InstructionType.branch,
                               "jbe": InstructionType.branch,
                               "jna": InstructionType.branch,
                               "ja": InstructionType.branch,
                               "jnbe": InstructionType.branch,
                               "jl": InstructionType.branch,
                               "jnge": InstructionType.branch,
                               "jge": InstructionType.branch,
                               "jnl": InstructionType.branch,
                               "jle": InstructionType.branch,
                               "jng": InstructionType.branch,
                               "jg": InstructionType.branch,
                               "jnle": InstructionType.branch,
                               "jp": InstructionType.branch,
                               "jpe": InstructionType.branch,
                               "jnp": InstructionType.branch,
                               "jpo": InstructionType.branch,
                               "jcxz": InstructionType.branch,
                               "jecxz": InstructionType.branch,
                               "jmp": InstructionType.branch,
                               "jmpq": InstructionType.branch,
                               "call" : InstructionType.call,
                               "callq" : InstructionType.call
                              }
        self.options = [
            ('Syntax Style', 'Switch between AT&T and Intel syntax', 'CHOICE', ('DEFAULT', 'intel-mnemonic', 'att-mnemonic')),
            ('Suffix', 'Always display instruction suffix in AT&T syntax', 'BOOL', ('DEFAULT','suffix', '')),
            ('Mode', 'Disassemble in 16bit mode, 32bit mode, or 64bit mode', 'CHOICE', ('DEFAULT','i8086', 'i386', 'x86-64')),
            ('Address Size', 'Assume 16bit, 32bit, or 64bit address size', 'CHOICE', ('DEFAULT','addr16', 'addr32', 'addr64')),
            ('Data Size', 'Assume 16bit or 32bit data size', 'CHOICE', ('DEFAULT','data16', 'data32')),
        ]
        
    def computeTargetAddr(self,inst):       
        #print repr( inst.opcode + " " + str(inst.instType) + " " + inst.operands)
        # Simple targets
        if (( inst.instType == InstructionType.call or \
              inst.instType == InstructionType.branch) and \
              len(inst.operands)>0 ):
            inst.isTargetAddrValid = False
            try: 
                # Watch out for pure address operands prefixed by '*'
                if inst.operands[0] == '*': 
                    inst.targetAddr = int(inst.operands[1:],16)
                else:
                    inst.targetAddr = int(inst.operands,16)
                inst.callType = callType.direct
                inst.isTargetAddrValid = True
            except: 
                inst.callType = callType.indirect

    def getMaxInstructionLenBytes(self):
        # Thanks Anthony!
        return 15
