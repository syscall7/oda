import logging

from oda.libs.odb.disassembler import ofd
import oda.libs.odb.disassembler.processors.processor
from oda.libs.odb.disassembler.processors.processor import get_processor
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.ops.scanners import FunctionScanner, BranchScanner, ParcelOffsetScanner

logger = logging.getLogger(__name__)

class PassiveScanOperation(Operation):

    def __init__(self, parcels = None):
        super(PassiveScanOperation, self).__init__()
        self.object_id = -1
        self.parcels = parcels

    def __str__(self):
        return "Passive scan operation"

    @staticmethod
    def deserialize(d):
        op = PassiveScanOperation()
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            # not going to store the parcels
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):
        assert (len(odb_file.get_structure_list(Parcel)) > 0)

        self.object_id = odb_file.get_object_id()
        analyzer = get_processor(odb_file.get_arch(), odb_file)

        function_scanner = FunctionScanner(analyzer, odb_file.get_structure_list(Symbol))
        branch_scanner = BranchScanner(analyzer)
        parcel_scanner = ParcelOffsetScanner()

        scanners = [
            function_scanner,
            branch_scanner,
            parcel_scanner
        ]

        lda_vma = 0

        parcels = self.parcels

        # if no parcels specified, operate on all
        if self.parcels is None:
            parcels = odb_file.get_structure_list(Parcel)

        parcels.sort(key=lambda p: p.vma_start, reverse=False)

        for parcel in parcels:

            logger.debug("parcel.vma_start=0x%08x parcel.vma_end=0x%08x" % (parcel.vma_start, parcel.vma_end))

            # initialize the logical display unit address

            the_ofd = ofd.Ofd(odb_file.get_binary())
            section = the_ofd.get_section_from_addr(parcel.vma_start)
            if not section:
                logger.error("Could not find section for addr 0x%08x" % parcel.vma_start)
                continue

            parcel.lda_start = lda_vma
            if parcel.is_code:

                def callback(addr, rawData, instr, abfd, self):
                    for scanner in scanners:
                        scanner.scan_line(addr, rawData, instr, abfd, parcel)


                the_ofd.disassemble(section.name, [], parcel.vma_start, parcel.vma_end,
                                    funcFmtLine=callback,
                                    funcFmtLineArgs={
                                        'self': self,
                                    })

            # account for the new display units
            lda_vma += parcel.num_ldas

        for scanner in scanners:
            scanner.commit(odb_file)