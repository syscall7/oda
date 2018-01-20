import logging

from oda.libs.odb.disassembler import ofd
from oda.libs.odb.disassembler.processors.processor import get_processor
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.function import Function
from oda.libs.odb.ops.scanners import FunctionScanner, BranchScanner, ParcelOffsetScanner, BadCodeScanner, HaltScanException
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation

logger = logging.getLogger(__name__)

class ActiveScanOperation(Operation):

    def __init__(self, vma):
        super(ActiveScanOperation, self).__init__()
        self.object_id = -1
        self.vma = vma

    def __str__(self):
        return "Converted code to data at address 0x%x" % self.vma

    @staticmethod
    def deserialize(d):
        op = ActiveScanOperation(d['vma'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
        }
        d.update(super().serialize())
        return d

    def _is_valid_instruction(self, the_ofd, analyzer, vma, end):
        """ Verify whether the given address points to a valid instruction or not """

        bad_code_scanner = BadCodeScanner(analyzer)
        section = the_ofd.get_section_from_addr(vma)

        the_ofd.disassemble(section.name, [], vma, end,
                            numLines=1,
                            funcFmtLine=bad_code_scanner.scan_line,
                            funcFmtLineArgs={'parcel': None})

        return bad_code_scanner.bad_addr is None

    def operate(self, odb_file):

        self.object_id = odb_file.get_object_id()

        analyzer = get_processor(odb_file.get_arch(), odb_file)
        the_ofd = ofd.Ofd(odb_file.get_binary())

        def convert_to_code(vma, odb_file, analyzer, the_ofd):

            parcels = ParcelList(odb_file.get_structure_list(Parcel))
            if len(parcels) == 0:
                raise Exception('Invalid operation: No parcels found')

            parcels_to_adjust = [p for p in parcels if p.vma_start > vma]

            p = parcels.find_parcel_by_vma(vma)

            if p is None:
                raise Exception('Invalid address: 0x%08x' % vma)

            # before doing anything, check if the given address starts with at least one valid instruction
            if not self._is_valid_instruction(the_ofd, analyzer, vma, p.vma_end):
                raise Exception("Failed to make code: invalid opcode")

            bad_code_scanner = BadCodeScanner(analyzer)
            function_scanner = FunctionScanner(analyzer, odb_file.get_structure_list(Symbol))
            branch_scanner = BranchScanner(analyzer)
            parcel_scanner = ParcelOffsetScanner()

            scanners = [
                # The parcel scanner must come first here, because we need it to 'push_vma' for the bad instruction, if
                # one is encountered
                parcel_scanner,
                bad_code_scanner,
                function_scanner,
                branch_scanner,
            ]

            # split the data parcel
            odb_file.execute(SplitParcelOperation(vma))

            parcels = ParcelList(odb_file.get_structure_list(Parcel))
            p = parcels.find_parcel_by_vma(vma)
            ldas_before_scan = p.size # one lda per byte

            def callback(addr, rawData, instr, abfd, self):
                for scanner in scanners:
                    scanner.scan_line(addr, rawData, instr, abfd, p)

            section = the_ofd.get_section_from_addr(vma)
            the_ofd.disassemble(section.name, [], vma, p.vma_end,
                                funcFmtLine=callback,
                                funcFmtLineArgs={
                                    'self': self,
                                    })

            ldas_removed = ldas_before_scan - p.num_ldas
            for p in parcels_to_adjust:
                p.lda_start -= ldas_removed

            for scanner in scanners:
                scanner.commit(odb_file)

            bad_addr = bad_code_scanner.bad_addr
            if bad_addr is not None:
                p = parcels.find_parcel_by_vma(bad_addr)
                odb_file.execute(SplitParcelOperation(bad_addr))

            #
            # consolidate the code parcels
            #
            parcels = ParcelList(odb_file.get_structure_list(Parcel))
            transaction = parcels.consolidate()

            # remove dead parcels
            for p in transaction.to_remove:
                odb_file.remove_item(p)

        convert_to_code(self.vma, odb_file, analyzer, the_ofd)

        # convert newly found functions to code as well
        following_new_funcs = True
        while following_new_funcs:
            funcs = odb_file.get_structure_list(Function)
            parcels = ParcelList(odb_file.get_structure_list(Parcel))

            # assume we are done unless we find at least one function that is within a data parcel
            following_new_funcs = False
            for f in funcs:
                p = parcels.find_parcel_by_vma(f.vma)

                if (  # if this function is at a valid address
                      (p is not None) and
                      # and the function is within a data parcel
                      (not p.is_code) and
                      # and the function looks to be valid code
                      self._is_valid_instruction(the_ofd, analyzer, f.vma, p.vma_end)
                ):

                    # convert this function to code
                    convert_to_code(f.vma, odb_file, analyzer, the_ofd)

                    # take another pass, in case we discovered new functions to disassemble
                    following_new_funcs = True

                    # break out of the for loop, but not the while
                    break

