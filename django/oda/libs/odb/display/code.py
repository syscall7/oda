import re
import logging

import bfd
from oda.libs.odb.display.base import DisplayGenerator, DisplayUnit
from oda.libs.odb.display.branchHTML import BranchLineHtmlFormatter
from oda.libs.odb.disassembler.processors.instruction import InstructionType, callType, RefUnit
from oda.libs.odb.structures import branch as branch_struct

logger = logging.getLogger(__name__)

class Function(object):
    def __init__(self, vma, name, type, xrefs):
        self.vma = vma
        self.xrefs = xrefs
        self.name = name
        self.type = type

def parseInstruction(addr, rawData, instr, abfd, self):

    rawInstrStr = ''
    instStr = ''
    du = DisplayUnit()
    du.isCode = True
    analyzer = self.context.analyzer
    labels = self.context.labels
    functions = self.context.functions

    # Separate out the address
    du.vma = addr

    # Separate out the raw bytes
    if abfd.bpc > 1 and (abfd.endian is bfd.ENDIAN_LITTLE or abfd.endian is bfd.ENDIAN_DEFAULT):
        du.rawBytes = ''.join(['%02x' % i for i in reversed(rawData)])
    else:
        du.rawBytes = ''.join(['%02x' % i for i in rawData])

    # Separate out the instruction and check for errors
    du.instStr = instr.replace('<', '&lt;').replace('>', '&gt;')

    matchObj = analyzer.errorInstRegEx.match(instr)
    if matchObj:
        du.isError = True

    # Get the Opcode
    if not du.isError:
        matchObj = analyzer.opcodeRegEx.match(instr)
        if matchObj:
            du.opcode = matchObj.group(1)
            du.instType = analyzer.getInstructionType(du.opcode)
            du.operands = matchObj.group(2)
            analyzer.computeTargetAddr(du)

            # Check if we need to create a label or function
            if du.isTargetAddrValid:

                # Create a new label for branch instructions
                if du.targetAddr not in labels and du.instType == InstructionType.branch:
                    labels.append(du.targetAddr)
                elif du.instType == InstructionType.call:
                    if du.targetAddr not in functions:
                        functions[du.targetAddr] = Function(du.targetAddr, 'func_%0.8x' % (du.targetAddr), 't', set([du.vma]))
                    else:
                        # Add new cross reference to set
                        functions[du.targetAddr].xrefs.update([du.vma])

            if du.instType == InstructionType.call or du.instType == InstructionType.branch:

                # If the branch target address is invalid
                if du.callType == callType.direct:

                    # Invalid target address
                    if not du.isTargetAddrValid:
                        du.instStr = "%-6s <errinsn>%s</errinsn>" % (du.opcode, du.operands)

                    # Valid target address
                    else:
                        # just use the opcode, we insert the target link on the client side (i.e. call some_func)
                        du.instStr = '%-7s' % du.opcode

            # Not a call/branch
            # TODO: Look for string references
            elif False:
                # for non-branch/non-call instructions, look for a reference to a string
                for m in re.finditer('0x([0-9a-fA-F]+)', du.instStr):
                    addrRef = int(m.group(1), 16)

                    # TODO: skip address 0 for now, but address this again someday
                    if 0 == addrRef:
                        continue
                    if addrRef in self.strings:
                        rawInstrStr += '  <a href="#/view/tab-assembly/vma/%08x" class="stringref">"%s"</a>' % (addrRef, self.strings[addrRef])
                instStr += rawInstrStr

            # Check for errors
            if du.isError:
                du.instStr = "<disline addr=%x><dislineerr>     %s</dislineerr></disline>" % (du.vma,du.instStr)


    du.section_name = self.context.section.name
    self.context.displayUnits[du.vma] = du

class CodeDisplayGenerator(DisplayGenerator):

    def display(self):

        displayUnits = self.context.displayUnits
        self.functions = self.context.functions
        self.labels = self.context.labels

        self.context.ofd.disassemble(self.context.section.name,
                                     self.context.options,
                                     self.context.cur_start,
                                     self.context.cur_end,
                                     numLines = self.context.maxLines,
                                     funcFmtLine=parseInstruction,
                                     funcFmtLineArgs={
                                          'self': self,
                                      })

        # Second Pass
        logger.debug("Analyze: START SECOND INSTRUCTION PASS. UNITS COUNT: %d" % (len(displayUnits)))

        # break up branches into sets based on function boundary
        prevFuncAddr = -1

        # sort displayUnits
        dunits = sorted(displayUnits.values(), key=lambda du: du.vma)

        # For now, we will ignore branching from/to other chunks of display units
        localBranches = list(filter(
            lambda b: (b.srcAddr > dunits[0].vma and b.srcAddr < dunits[-1].vma) and
                      (b.targetAddr > dunits[0].vma and b.targetAddr < dunits[-1].vma),
            self.context.odb_file.get_structure_list(branch_struct.Branch)))

        # Get the branch lines
        if len(self.functions) > 0 and len(dunits) > 0:
            # Ignore functions outside of the display units we retrieved
            functions = filter(lambda f: f.vma > dunits[0].vma and f.vma < dunits[-1].vma, self.functions.values())
            for function in sorted(functions, key=lambda f: f.vma):
                # get all the branches between prev func and this func
                branches = [b for b in localBranches if b.targetAddr > prevFuncAddr and b.targetAddr < function.vma]

                dus = [du for du in dunits if du.vma >= prevFuncAddr and du.vma < function.vma]

                self.displayLabels(dus, branches)
                prevFuncAddr = function.vma

            # now process between the last func and the end
            branches = [b for b in localBranches if b.targetAddr >= prevFuncAddr]
            dus = [du for du in dunits if du.vma >= prevFuncAddr]
            self.displayLabels(dus, branches)

        else:
            self.displayLabels(dunits, localBranches)


        logger.debug("Analyze: SECOND PASS COMPLETE")

    def displayLabels(self, dunits, branches):

        for du in dunits:
            if du.isTargetAddrValid:
                vma = du.targetAddr
                if du.targetAddr in self.functions:
                    du.targetRef = RefUnit(vma)
                elif du.targetAddr in self.labels:
                    du.targetRef = RefUnit(vma)

            if du.vma in self.functions:
                du.isFunction = True
                du.branchRef = RefUnit(du.vma)
                for xref in sorted(self.functions[du.vma].xrefs):
                    du.crossRef.append(RefUnit( xref))

            elif du.vma in self.labels:
                du.branchRef = RefUnit(du.vma)
                du.isBranch = True
