import logging
from oda.libs.odb.binaries import BinaryString
from oda.libs.odb.structures.branch import Branch
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.parcel import ParcelList, Parcel
from oda.libs.odb.disassembler.disassembler import Disassembler

logger = logging.getLogger(__name__)

class BranchGraphNode:
    def __init__(self, startAddr, endAddr, size, yesAddr, noAddr):
        self.startAddr = startAddr   # starting address of this block
        self.endAddr = endAddr       # location of the branch (i.e., the last instruction of this block)
        self.yesAddr = yesAddr       # location to branch to if branch is taken
        self.noAddr = noAddr         # location to branch to if branch is not taken (i.e., next instruction)
        self.size = size             # number of bytes in this block

    def split(self, vma, parcels):
        if (vma not in self) or (vma == self.startAddr):
            raise Exception("Invalid attempt to split a node")

        newSelfSize = vma - self.startAddr
        newNode = BranchGraphNode(vma, self.endAddr, self.size - newSelfSize, self.yesAddr, self.noAddr)
        self.endAddr = parcels.lda_to_vma(parcels.vma_to_lda(vma-1))
        self.yesAddr = vma
        self.noAddr = None
        self.size = newSelfSize

        return newNode

    def getId(self):
        return '0x%x' % self.startAddr
    id = property(getId)

    def __contains__(self, vma):
        try:
            return (vma >= self.startAddr) and (vma <= self.endAddr)
        except TypeError:
            logger.warning("looking for empty VMA in BranchGraphNode")
            return False

    def __repr__(self):
        no = '0x%08x' % self.noAddr if self.noAddr else 'None'
        yes = '0x%08x' % self.yesAddr if self.yesAddr else 'None'
        return "%s  0x%08x--0x%08x Yes:%s, No:%s %d bytes" % (self.__class__, self.startAddr, self.endAddr, yes, no, self.size)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class BranchGraphView(list):

    def __init__(self, odb_file, vma):
        self.odb_file = odb_file
        start = None
        end = None
        self.parcels = ParcelList(odb_file.get_structure_list(Parcel))

        # first, some validation
        p = self.parcels.find_parcel_by_vma(vma)
        if p:
            # initialize to parcel boundaries
            start = p.vma_start
            end = p.vma_end

            # if this is not in a code section
            if not p.is_code:
                raise Exception("Graph view is not available for data sections!")

        # else, invalid address
        else:
            raise Exception("Graph view is not available for invalid address 0x%x!" % vma)

        if type(odb_file.binary) == BinaryString:
            # TODO: Handle nonzero base address
            start = 0
            end = odb_file.binary.size

        functions = sorted(odb_file.get_structure_list(Function), key=lambda f: f.vma)
        for f in functions:
            if vma >= f.vma:
                start = f.vma
            elif vma < f.vma:
                end = f.vma
                break

        # get all the branches within this function
        # TODO: Deal with indirect branches (i.e., jmp rax)
        branches = filter(lambda b: b.srcAddr >= start and b.srcAddr < end and
                                    b.targetAddr >= start and b.targetAddr < end,
                            odb_file.get_structure_list(Branch))

        # dict of nodes, keyed by starting address of the block
        self._nodes = {}
        thisBlock = start

        for b in sorted(branches, key=lambda b: b.srcAddr):
            # address if the branch is not taken (i.e., the addr of the next instruction)
            no = b.srcAddr + b.instrLen

            # address if the branch is taken
            yes = b.targetAddr

            # first node
            self._nodes[thisBlock] = BranchGraphNode(thisBlock, b.srcAddr, no - thisBlock, yes, no)

            # advance to next block
            thisBlock = no

        # make last block
        if thisBlock != end:
            end_line = self.parcels.vma_to_lda(end-1)
            last_addr = self.parcels.lda_to_vma(end_line)
            self._nodes[thisBlock] = BranchGraphNode(thisBlock, last_addr, end - thisBlock, None, None)

        # for each target 'yes' branch address
        # NOTE: The 'no' branch addresses are guaranteed to be nodes by this point
        # NOTE: We can't iterate over the nodes with iteritems() since we modify the dictionary in the loop
        for addr in [n.yesAddr for n in self._nodes.values()]:
            # if this is a new node
            if addr not in self._nodes:
                # find the node that contains this address (the parent) and split it
                for parent in list(self._nodes.values()):
                    if addr in parent:
                        newNode = parent.split(addr, self.parcels)
                        self._nodes[addr] = newNode

    '''
    {
        nodes:
        [
            {id:X, instructions: [du1, du2, du3, du4 ... }
            {id:Y, instructions: [du9, du10, du11 .... }
            ....
        ]
        links: [
            { from:x, to:y, type: 'taken' }
            { from:y, to: z, type: 'notTaken'}
            { from:o, to: q, type: 'unconditional'}
        ]
    }
    '''
    def getNodes(self):

        dasm = Disassembler(self.odb_file)

        # convert _nodes to representation needed by front end
        nodes = []
        for startAddr, node in self._nodes.items():
            startLine = self.parcels.vma_to_lda(startAddr)
            endLine = self.parcels.vma_to_lda(startAddr + node.size)
            if endLine is None:
                endLine = self.parcels.sum_ldas()
            dus = dasm.display(startAddr, endLine - startLine, False)
            nodes.append({'id': node.id, 'instructions': dus})

        return nodes

    def getLinks(self):
        links = []
        # convert _nodes to representation needed by front end
        for startAddr, node in self._nodes.items():
            try:
                if node.noAddr:
                    links.append({'from': node.id, 'to': self._nodes[node.noAddr].id, 'type': 'notTaken'})
                    links.append({'from': node.id, 'to': self._nodes[node.yesAddr].id, 'type': 'taken'})
                elif node.yesAddr:
                    links.append({'from': node.id, 'to': self._nodes[node.yesAddr].id, 'type': 'unconditional'})
                else:
                    # else, this is the last node in the function, which has no links
                    pass
            except Exception as e:
                # for now, keep going if something goes wrong
                # AVD@9/8/15: An exception can happen right now if the last instruction in the function is a
                #             branch to somewhere in the middle of the function.  The problem is that the "no"
                #             address is not within the function, since it is actually the first instruction of
                #             the next function.  Need to revisit this and see if we can do better than just
                #             skipping this link.
                continue

        return links

    nodes = property(getNodes)
    links = property(getLinks)


