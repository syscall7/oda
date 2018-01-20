'''
Created on November 7, 2012

@author: Owner
'''
import re

from oda.libs.odb.disassembler.processors.processor import Processor
from oda.libs.odb.disassembler.processors.processor import InstructionType, callType


class arm(Processor):
    '''
    classdocs
    '''

    def __init__(self, odb_file):
        Processor.__init__(self, odb_file)

        self.options = [
            ('Force Thumb Mode', 'Assume all insns are Thumb insns', 'CHOICE', ('DEFAULT','force-thumb', 'no-force-thumb'), False),
            ('Register Names', 'Select register names specified by ATPCS, APCS, ARM ISA, gcc, or raw', 'CHOICE', 
                ('DEFAULT','reg-names-special-atpcs', 'reg-names-atpcs', 'reg-names-apcs', 'reg-names-std', 'reg-names-gcc', 'reg-names-raw'), 'reg-names-gcc'),
        ]

        self.opcodeRegExStr = "^([\w\.]+)\s+([^<]+)"

        self.opcodeTypes = {   
                               "b" : InstructionType.branch,
                               "beq" : InstructionType.branch,
                               "bne" : InstructionType.branch,
                               "bcs" : InstructionType.branch,
                               "bcc" : InstructionType.branch,
                               "bmi" : InstructionType.branch,
                               "bpl" : InstructionType.branch,
                               "bvs" : InstructionType.branch,
                               "bvc" : InstructionType.branch,
                               "bhi" : InstructionType.branch,
                               "bls" : InstructionType.branch,
                               "bge" : InstructionType.branch,
                               "blt" : InstructionType.branch,
                               "bgt" : InstructionType.branch,
                               "ble" : InstructionType.branch,
                               "bal" : InstructionType.branch,

                               "bl" : InstructionType.call,
                               "bleq" : InstructionType.call,
                               "blne" : InstructionType.call,
                               "blcs" : InstructionType.call,
                               "blcc" : InstructionType.call,
                               "blmi" : InstructionType.call,
                               "blpl" : InstructionType.call,
                               "blvs" : InstructionType.call,
                               "blvc" : InstructionType.call,
                               "blhi" : InstructionType.call,
                               "blls" : InstructionType.call,
                               "blge" : InstructionType.call,
                               "bllt" : InstructionType.call,
                               "blgt" : InstructionType.call,
                               "blle" : InstructionType.call,
                               "blal" : InstructionType.call,
                               
                               "bx" : InstructionType.call,
                               "bxeq" : InstructionType.call,
                               "bxne" : InstructionType.call,
                               "bxcs" : InstructionType.call,
                               "bxcc" : InstructionType.call,
                               "bxmi" : InstructionType.call,
                               "bxpl" : InstructionType.call,
                               "bxvs" : InstructionType.call,
                               "bxvc" : InstructionType.call,
                               "bxhi" : InstructionType.call,
                               "bxls" : InstructionType.call,
                               "bxge" : InstructionType.call,
                               "bxlt" : InstructionType.call,
                               "bxgt" : InstructionType.call,
                               "bxle" : InstructionType.call,
                               "bxal" : InstructionType.call,

                               "b.n" : InstructionType.branch,
                               "beq.n" : InstructionType.branch,
                               "bne.n" : InstructionType.branch,
                               "bcs.n" : InstructionType.branch,
                               "bcc.n" : InstructionType.branch,
                               "bmi.n" : InstructionType.branch,
                               "bpl.n" : InstructionType.branch,
                               "bvs.n" : InstructionType.branch,
                               "bvc.n" : InstructionType.branch,
                               "bhi.n" : InstructionType.branch,
                               "bls.n" : InstructionType.branch,
                               "bge.n" : InstructionType.branch,
                               "blt.n" : InstructionType.branch,
                               "bgt.n" : InstructionType.branch,
                               "ble.n" : InstructionType.branch,
                               "bal.n" : InstructionType.branch,

                               "bl.n" : InstructionType.call,
                               "bleq.n" : InstructionType.call,
                               "blne.n" : InstructionType.call,
                               "blcs.n" : InstructionType.call,
                               "blcc.n" : InstructionType.call,
                               "blmi.n" : InstructionType.call,
                               "blpl.n" : InstructionType.call,
                               "blvs.n" : InstructionType.call,
                               "blvc.n" : InstructionType.call,
                               "blhi.n" : InstructionType.call,
                               "blls.n" : InstructionType.call,
                               "blge.n" : InstructionType.call,
                               "bllt.n" : InstructionType.call,
                               "blgt.n" : InstructionType.call,
                               "blle.n" : InstructionType.call,
                               "blal.n" : InstructionType.call,
                               
                               "bx.n" : InstructionType.call,
                               "bxeq.n" : InstructionType.call,
                               "bxne.n" : InstructionType.call,
                               "bxcs.n" : InstructionType.call,
                               "bxcc.n" : InstructionType.call,
                               "bxmi.n" : InstructionType.call,
                               "bxpl.n" : InstructionType.call,
                               "bxvs.n" : InstructionType.call,
                               "bxvc.n" : InstructionType.call,
                               "bxhi.n" : InstructionType.call,
                               "bxls.n" : InstructionType.call,
                               "bxge.n" : InstructionType.call,
                               "bxlt.n" : InstructionType.call,
                               "bxgt.n" : InstructionType.call,
                               "bxle.n" : InstructionType.call,
                               "bxal.n" : InstructionType.call,


                               "b.w" : InstructionType.branch,
                               "beq.w" : InstructionType.branch,
                               "bne.w" : InstructionType.branch,
                               "bcs.w" : InstructionType.branch,
                               "bcc.w" : InstructionType.branch,
                               "bmi.w" : InstructionType.branch,
                               "bpl.w" : InstructionType.branch,
                               "bvs.w" : InstructionType.branch,
                               "bvc.w" : InstructionType.branch,
                               "bhi.w" : InstructionType.branch,
                               "bls.w" : InstructionType.branch,
                               "bge.w" : InstructionType.branch,
                               "blt.w" : InstructionType.branch,
                               "bgt.w" : InstructionType.branch,
                               "ble.w" : InstructionType.branch,
                               "bal.w" : InstructionType.branch,

                               "bl.w" : InstructionType.call,
                               "bleq.w" : InstructionType.call,
                               "blne.w" : InstructionType.call,
                               "blcs.w" : InstructionType.call,
                               "blcc.w" : InstructionType.call,
                               "blmi.w" : InstructionType.call,
                               "blpl.w" : InstructionType.call,
                               "blvs.w" : InstructionType.call,
                               "blvc.w" : InstructionType.call,
                               "blhi.w" : InstructionType.call,
                               "blls.w" : InstructionType.call,
                               "blge.w" : InstructionType.call,
                               "bllt.w" : InstructionType.call,
                               "blgt.w" : InstructionType.call,
                               "blle.w" : InstructionType.call,
                               "blal.w" : InstructionType.call,
                               
                               "bx.w" : InstructionType.call,
                               "bxeq.w" : InstructionType.call,
                               "bxne.w" : InstructionType.call,
                               "bxcs.w" : InstructionType.call,
                               "bxcc.w" : InstructionType.call,
                               "bxmi.w" : InstructionType.call,
                               "bxpl.w" : InstructionType.call,
                               "bxvs.w" : InstructionType.call,
                               "bxvc.w" : InstructionType.call,
                               "bxhi.w" : InstructionType.call,
                               "bxls.w" : InstructionType.call,
                               "bxge.w" : InstructionType.call,
                               "bxlt.w" : InstructionType.call,
                               "bxgt.w" : InstructionType.call,
                               "bxle.w" : InstructionType.call,
                               "bxal.w" : InstructionType.call,
                                                           
                              }

    def computeTargetAddr(self,inst):       
        
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
        return 4