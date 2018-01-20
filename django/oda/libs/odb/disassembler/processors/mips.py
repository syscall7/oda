'''
Created on November 7, 2012

@author: Owner
'''
import re

from oda.libs.odb.disassembler.processors.processor import Processor
from oda.libs.odb.disassembler.processors.processor import InstructionType, callType


class mips(Processor):
    '''
    classdocs
    '''

    ABI_OPTS = ('numeric', '32', 'n32', '64')

    ARCH_OPTS = ('numeric', 'r3000', 'r3900', 'r4000', 'r4010', 'vr4100',
                 'vr4111', 'vr4120', 'r4300', 'r4400', 'r4600', 'r4650',
                 'r5000', 'vr5400', 'vr5500', 'r6000', 'rm7000', 'rm9000',
                 'r8000', 'r10000', 'r12000', 'r14000', 'r16000', 'mips5',
                 'mips32', 'mips32r2', 'mips64', 'mips64r2', 'sb1',
                 'loongson2e', 'loongson2f', 'loongson3a', 'octeon',
                 'octeon+', 'octeon2', 'xlr', 'xlp')

    def __init__(self, odb_file):
        Processor.__init__(self, odb_file)

        self.options = [
            ('ABI', 'Naming style used for gpr and fpr registers', 'CHOICE', self.ABI_OPTS + ('DEFAULT',),  ''),
            ('ARCH', 'Naming style used for cp0 and hwr registers', 'CHOICE', self.ARCH_OPTS + ('DEFAULT',), ''),
        ]
        
        self.opcodeTypes = {   
                               "b" : InstructionType.branch,
                               "bal" : InstructionType.branch,
                               "beq" : InstructionType.branch,
                               "beqz" : InstructionType.branch,
                               "bgez" : InstructionType.branch,
                               "bgezal" : InstructionType.branch,
                               "bgtz" : InstructionType.branch,
                               "blez" : InstructionType.branch,
                               "bltz" : InstructionType.branch,
                               "bltzal" : InstructionType.branch,
                               "bne" : InstructionType.branch,
                               "bnez" : InstructionType.branch,
                               "j" : InstructionType.branch,
                               "jal" : InstructionType.call,
                               "jalr" : InstructionType.call,
                               "jr" : InstructionType.call,
                              }

    def processOptions(self, options):
        '''
        Below are the options that mips accepts:
            gpr-names=ABI
            fpr-names=ABI
            reg-names=ABI
            cp0-names=ARCH
            hwr-names=ARCH
            reg-names=ARCH

        In this function we translate our simplified options that are exposed to the user (ABI and ARCH) to the
        format expected by libopcodes.

        NOTE: Because 'numeric' is both an ARCH and an ABI option, the solution below is less than ideal.  That's
              because if a user selects numeric for ABI, they will get numeric for both ARCH and ABI.  Whaddya expect,
              this is a free tool!
        '''
        new_options = options[:]
        for opt in options:
            if opt in self.ABI_OPTS:
                new_options.append('gpr-names=%s' % opt)
                new_options.append('fpr-names=%s' % opt)
                new_options.append('reg-names=%s' % opt)

            if opt in self.ARCH_OPTS:
                new_options.append('cp0-names=%s,' % opt)
                new_options.append('hwr-names=%s,' % opt)
                new_options.append('reg-names=%s,' % opt)

            if opt in self.ARCH_OPTS or opt in self.ABI_OPTS:
                new_options.remove(opt)

        return new_options

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
