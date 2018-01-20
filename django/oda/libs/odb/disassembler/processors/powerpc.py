'''
Created on November 7, 2012

@author: Owner
'''
import re

from oda.libs.odb.disassembler.processors.processor import Processor
from oda.libs.odb.disassembler.processors.processor import InstructionType, callType


class powerpc(Processor):
    '''
    classdocs
    '''

    def __init__(self, odb_file):
        Processor.__init__(self, odb_file)

        self.options = [
            ('Mode', 'Processor mode', 'CHOICE', ('DEFAULT', '32', '64'), ''),
            ('CPU', 'CPU variant', 'CHOICE',
                ('DEFAULT', '403', '405', '440', '464', '476', '601', '603', '604',
                 '620', '7400', '7410', '7450', '7455', '750cl', 'a2', 
                 'altivec', 'any', 'booke', 'booke32', 'cell', 'com', 'e300',
                 'e500','e500mc','e500mc64', 'e5500', 'e6500', 'e500x2', 
                 'efs', 'power4', 'power5', 'power6', 'power7', 'ppc', 'ppc32', 
                 'ppc64', 'ppc64bridge', 'ppcps', 'pwr', 'pwr2', 'pwr4', 
                 'pwr5', 'pwr5x', 'pwr6', 'pwr7', 'pwrx', 'spe', 'titan', 
                 'vle', 'vsx'), ''),
        ]

        self.opcodeTypes = {   
                               "b" : InstructionType.branch,
                               "ba" : InstructionType.branch,
                               "bc" : InstructionType.branch,
                               "bca" : InstructionType.branch,
                               "bcl" : InstructionType.call,
                               "bcla" : InstructionType.call,
                               "bclr" : InstructionType.call,
                               "bclrl" : InstructionType.call,
                               "bcctr" : InstructionType.branch,
                               "bcctrl" : InstructionType.call,
                               "bl" : InstructionType.call,
                               "bla" : InstructionType.call,
                               
                               "blt" : InstructionType.branch,
                               "ble" : InstructionType.branch,
                               "beq" : InstructionType.branch,
                               "bge" : InstructionType.branch,
                               "bgt" : InstructionType.branch,
                               "bnl" : InstructionType.branch,
                               "bne" : InstructionType.branch,
                               "bng" : InstructionType.branch,
                               "bso" : InstructionType.branch,
                               "bns" : InstructionType.branch,
                               "bun" : InstructionType.branch,
                               "bnu" : InstructionType.branch,
                               
                               "bltlr" : InstructionType.branch,
                               "blelr" : InstructionType.branch,
                               "beqlr" : InstructionType.branch,
                               "bgelr" : InstructionType.branch,
                               "bgtlr" : InstructionType.branch,
                               "bnllr" : InstructionType.branch,
                               "bnelr" : InstructionType.branch,
                               "bnglr" : InstructionType.branch,
                               "bsolr" : InstructionType.branch,
                               "bnslr" : InstructionType.branch,
                               "bunlr" : InstructionType.branch,
                               "bnulr" : InstructionType.branch,
                               
                               "bltctr" : InstructionType.branch,
                               "blectr" : InstructionType.branch,
                               "beqctr" : InstructionType.branch,
                               "bgectr" : InstructionType.branch,
                               "bgtctr" : InstructionType.branch,
                               "bnlctr" : InstructionType.branch,
                               "bnectr" : InstructionType.branch,
                               "bngctr" : InstructionType.branch,
                               "bsoctr" : InstructionType.branch,
                               "bnsctr" : InstructionType.branch,
                               "bunctr" : InstructionType.branch,
                               "bnuctr" : InstructionType.branch,

                               "bltl" : InstructionType.call,
                               "blel" : InstructionType.call,
                               "beql" : InstructionType.call,
                               "bgel" : InstructionType.call,
                               "bgtl" : InstructionType.call,
                               "bnll" : InstructionType.call,
                               "bnel" : InstructionType.call,
                               "bngl" : InstructionType.call,
                               "bsol" : InstructionType.call,
                               "bnsl" : InstructionType.call,
                               "bunl" : InstructionType.call,
                               "bnul" : InstructionType.call,

                               "bltla" : InstructionType.call,
                               "blela" : InstructionType.call,
                               "beqla" : InstructionType.call,
                               "bgela" : InstructionType.call,
                               "bgtla" : InstructionType.call,
                               "bnlla" : InstructionType.call,
                               "bnela" : InstructionType.call,
                               "bngla" : InstructionType.call,
                               "bsola" : InstructionType.call,
                               "bnsla" : InstructionType.call,
                               "bunla" : InstructionType.call,
                               "bnula" : InstructionType.call,

                               "bltlrl" : InstructionType.call,
                               "blelrl" : InstructionType.call,
                               "beqlrl" : InstructionType.call,
                               "bgelrl" : InstructionType.call,
                               "bgtlrl" : InstructionType.call,
                               "bnllrl" : InstructionType.call,
                               "bnelrl" : InstructionType.call,
                               "bnglrl" : InstructionType.call,
                               "bsolrl" : InstructionType.call,
                               "bnslrl" : InstructionType.call,
                               "bunlrl" : InstructionType.call,
                               "bnulrl" : InstructionType.call,

                               "bltctrl" : InstructionType.call,
                               "blectrl" : InstructionType.call,
                               "beqctrl" : InstructionType.call,
                               "bgectrl" : InstructionType.call,
                               "bgtctrl" : InstructionType.call,
                               "bnlctrl" : InstructionType.call,
                               "bnectrl" : InstructionType.call,
                               "bngctrl" : InstructionType.call,
                               "bsoctrl" : InstructionType.call,
                               "bnsctrl" : InstructionType.call,
                               "bunctrl" : InstructionType.call,
                               "bnuctrl" : InstructionType.call,
                               
                              }
        self.opcodeRegExStr = "^([-\w\+]+)\s+([^<]+)"

    def getInstructionType(self,opcode):
        if opcode[-1] == '-' or opcode[-1] == '+':
            opcode = opcode[:-1]
        if opcode in self.opcodeTypes:
            return self.opcodeTypes[opcode]
        return InstructionType.normal

    def makeInstrBranch(self, inst, labelName):
        operands = inst.operands.split(',')
        operands[-1] = "<a href=\"#view/tab-assembly/vma/%08x\">%s</a>" % (inst.targetAddr,labelName)
        operands_str = ",".join(operands)
        return "%-8s%s" % (inst.opcode, operands_str)

    def computeTargetAddr(self,inst):       
        
        # Simple targets
        if (( inst.instType == InstructionType.call or \
              inst.instType == InstructionType.branch) and \
              len(inst.operands)>0 ):
            inst.isTargetAddrValid = False
            operands = inst.operands.split(',')
            try: 
                # The last operand is the immediate
                inst.targetAddr = int(operands[-1],16)
                inst.callType = callType.direct
                inst.isTargetAddrValid = True
            except: 
                inst.callType = callType.indirect

    def getMaxInstructionLenBytes(self):
        return 4