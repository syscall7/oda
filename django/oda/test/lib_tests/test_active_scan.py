import os
from oda.libs.odb.binaries import BinaryFile

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.active_scan_operation import ActiveScanOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.parcel import Parcel, ParcelList
from oda.test.oda_test_case import OdaLibTestCase

class TestActiveScanOperation(OdaLibTestCase):

    # this is a simple data->code conversion at address 0x4002ce that creates 3 instructions in the .gnu.hash section
    def test_basic_active_scan(self):

        # we load this ELF as a raw binary, because it has an invalid opcode fairly early on
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('mkdir'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))
        p = parcels_before.find_parcel_by_vma(0x4002ce)
        gnu_hash_lda_before = parcels_before.vma_to_lda(0x4002cd)
        dynsym_lda_before = parcels_before.vma_to_lda(0x4002e0)
        dynstr_lda_before = parcels_before.vma_to_lda(0x400a18)

        # number of parcels before the split
        self.assertEquals(24, len(parcels_before))

        # execute the split operation
        odb_file.execute(ActiveScanOperation(0x4002ce))

        # number of parcels after the split
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(26, len(parcels_after))

        # get the three parcels
        p1 = parcels_after.find_parcel_by_vma(0x400298)
        p2 = parcels_after.find_parcel_by_vma(0x4002ce)
        p3 = parcels_after.find_parcel_by_vma(0x4002d5)

        # make sure they are all unique
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)

        # check num_ldas in p1 (54 bytes)
        self.assertEquals(54, p1.num_ldas)

        # check num_ldas in p2 (3 instructions)
        self.assertEquals(3, p2.num_ldas)

        # check num_ldas in p3 (7 bytes)
        self.assertEquals(7, p3.num_ldas)

        # make sure vmas line up
        self.assertEquals(0x400298, p1.vma_start)
        self.assertEquals(0x4002ce, p1.vma_end)
        self.assertEquals(0x4002ce, p2.vma_start)
        self.assertEquals(0x4002d5, p2.vma_end)
        self.assertEquals(0x4002d5, p3.vma_start)
        self.assertEquals(0x4002dc, p3.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(gnu_hash_lda_before, parcels_after.vma_to_lda(0x4002cd))
        self.assertEquals(gnu_hash_lda_before+1, parcels_after.vma_to_lda(0x4002ce))
        self.assertEquals(False, p1.is_code)
        self.assertEquals(False, p3.is_code)

        # these changed
        self.assertEquals(gnu_hash_lda_before+2, parcels_after.vma_to_lda(0x4002d0))
        self.assertEquals(gnu_hash_lda_before+3, parcels_after.vma_to_lda(0x4002d2))

        self.assertEquals(gnu_hash_lda_before+4, parcels_after.vma_to_lda(0x4002d5))
        self.assertEquals(gnu_hash_lda_before+5, parcels_after.vma_to_lda(0x4002d6))
        self.assertEquals(gnu_hash_lda_before+6, parcels_after.vma_to_lda(0x4002d7))
        self.assertEquals(gnu_hash_lda_before+7, parcels_after.vma_to_lda(0x4002d8))
        self.assertEquals(gnu_hash_lda_before+8, parcels_after.vma_to_lda(0x4002d9))
        self.assertEquals(gnu_hash_lda_before+9, parcels_after.vma_to_lda(0x4002da))
        self.assertEquals(gnu_hash_lda_before+10,parcels_after.vma_to_lda(0x4002db))
        self.assertEquals(True, p2.is_code)

        # 7 bytes turned into 3 instructions, so it shifted the following parcels by -4 ldas
        self.assertEquals(dynsym_lda_before-4, parcels_after.vma_to_lda(0x4002e0))
        self.assertEquals(dynstr_lda_before-4, parcels_after.vma_to_lda(0x400a18))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x4002cd, parcels_after.lda_to_vma(gnu_hash_lda_before))
        self.assertEquals(0x4002ce, parcels_after.lda_to_vma(gnu_hash_lda_before+1))

        # these changed
        self.assertEquals(0x4002d0, parcels_after.lda_to_vma(gnu_hash_lda_before+2))
        self.assertEquals(0x4002d2, parcels_after.lda_to_vma(gnu_hash_lda_before+3))

        self.assertEquals(0x4002d5, parcels_after.lda_to_vma(gnu_hash_lda_before+4))
        self.assertEquals(0x4002d6, parcels_after.lda_to_vma(gnu_hash_lda_before+5))
        self.assertEquals(0x4002d7, parcels_after.lda_to_vma(gnu_hash_lda_before+6))
        self.assertEquals(0x4002d8, parcels_after.lda_to_vma(gnu_hash_lda_before+7))
        self.assertEquals(0x4002d9, parcels_after.lda_to_vma(gnu_hash_lda_before+8))
        self.assertEquals(0x4002da, parcels_after.lda_to_vma(gnu_hash_lda_before+9))
        self.assertEquals(0x4002db, parcels_after.lda_to_vma(gnu_hash_lda_before+10))

        # 7 bytes turned into 3 instructions, so it shifted the following parcels by -4 ldas
        self.assertEquals(0x4002e0, parcels_after.lda_to_vma(dynsym_lda_before-4))
        self.assertEquals(0x400a18, parcels_after.lda_to_vma(dynstr_lda_before-4))

    # this is a more complex data->code conversion that follows call instructions to discover new code regions
    def test_follow_calls_i386(self):

        odb_file = OdbFile(BinaryFile(
            self.get_test_bin_path('active_scan_follow_calls/active_scan_follow_calls.bin'), 'binary', 'i386'))

        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))

        # number of parcels before the split
        self.assertEquals(1, len(parcels_before))

        # execute the active scan operation
        odb_file.execute(ActiveScanOperation(0x0))

        # number of parcels after the split
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(11, len(parcels_after))

    # this is a more complex data->code conversion that follows jmp instructions to discover new code regions
    def failing_test_follow_jmps_i386(self):

        odb_file = OdbFile(BinaryFile(
            self.get_test_bin_path('active_scan_follow_jmps/active_scan_follow_jmps.bin'), 'binary', 'i386'))

        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))

        # number of parcels before the split
        self.assertEquals(1, len(parcels_before))

        # execute the active scan operation
        odb_file.execute(ActiveScanOperation(0x0))

        # number of parcels after the split
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(11, len(parcels_after))
