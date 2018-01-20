import os
from oda.libs.odb.binaries import BinaryFile

from oda.libs.odb.odb_file import OdbFile
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.split_parcel_operation import SplitParcelOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation
from oda.libs.odb.structures.parcel import Parcel, ParcelList, DataParcel, CodeParcel
from oda.test.oda_test_case import OdaLibTestCase

class TestParcels(OdaLibTestCase):

    def test_split_to_data_basic(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))
        p = parcels_before.find_parcel_by_vma(0x4029c0)
        num_p1_ldas_before = p.num_ldas
        text_lda_before = parcels_before.vma_to_lda(0x4029c0)
        fini_lda_before = parcels_before.vma_to_lda(0x412bec)

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x4029d5))

        # number of parcels after the split
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(27, len(parcels_after))

        # get the three parcels
        p1 = parcels_after.find_parcel_by_vma(0x4029c0)
        p2 = parcels_after.find_parcel_by_vma(0x4029d5)
        p3 = parcels_after.find_parcel_by_vma(0x4029da)

        # make sure they are all unique
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)

        # check num_ldas in p1 (5 instructions)
        self.assertEquals(5, p1.num_ldas)

        # check num_ldas in p2 (this one instruction has now become 5 data bytes)
        self.assertEquals(5, p2.num_ldas)

        # check num_ldas in p3 (less 5 from p1 and less 1 from p2 - remember it used to only be 1 lda before the split)
        self.assertEquals(num_p1_ldas_before - 5 - 1, p3.num_ldas)

        # make sure vmas line up
        self.assertEquals(0x4029c0, p1.vma_start)
        self.assertEquals(0x4029d5, p1.vma_end)
        self.assertEquals(0x4029d5, p2.vma_start)
        self.assertEquals(0x4029da, p2.vma_end)
        self.assertEquals(0x4029da, p3.vma_start)
        self.assertEquals(0x412bec, p3.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(text_lda_before, parcels_after.vma_to_lda(0x4029c0))
        self.assertEquals(text_lda_before+5, parcels_after.vma_to_lda(0x4029d5))
        self.assertEquals(True, p1.is_code)
        self.assertEquals(True, p3.is_code)

        # these changed
        self.assertEquals(text_lda_before+6, parcels_after.vma_to_lda(0x4029d6))
        self.assertEquals(text_lda_before+7, parcels_after.vma_to_lda(0x4029d7))
        self.assertEquals(text_lda_before+8, parcels_after.vma_to_lda(0x4029d8))
        self.assertEquals(text_lda_before+9, parcels_after.vma_to_lda(0x4029d9))
        self.assertEquals(text_lda_before+10, parcels_after.vma_to_lda(0x4029da))
        self.assertEquals(text_lda_before+11, parcels_after.vma_to_lda(0x4029db))
        self.assertEquals(False, p2.is_code)

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(fini_lda_before+4, parcels_after.vma_to_lda(0x412bec))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x4029c0, parcels_after.lda_to_vma(text_lda_before))
        self.assertEquals(0x4029d5, parcels_after.lda_to_vma(text_lda_before+5))

        # these changed
        self.assertEquals(0x4029d6, parcels_after.lda_to_vma(text_lda_before+6))
        self.assertEquals(0x4029d7, parcels_after.lda_to_vma(text_lda_before+7))
        self.assertEquals(0x4029d8, parcels_after.lda_to_vma(text_lda_before+8))
        self.assertEquals(0x4029d9, parcels_after.lda_to_vma(text_lda_before+9))
        self.assertEquals(0x4029da, parcels_after.lda_to_vma(text_lda_before+10))
        self.assertEquals(0x4029db, parcels_after.lda_to_vma(text_lda_before+11))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(0x412bec, parcels_after.lda_to_vma(fini_lda_before+4))

    def test_split_to_data_at_start_of_parcel(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))

        # start of .fini section
        p = parcels_before.find_parcel_by_vma(0x412bec)
        num_p1_ldas_before = p.num_ldas
        fini_lda_before = parcels_before.vma_to_lda(0x412bec)

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x412bec))

        # number of parcels after the split (should only add one more)
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(26, len(parcels_after))

        # get the two parcels
        p1 = parcels_after.find_parcel_by_vma(0x412bec)
        p2 = parcels_after.find_parcel_by_vma(0x412bf0)

        # make sure they are unique
        self.assertNotEqual(p1, p2)

        # check num_ldas in p1 (4 data bytes)
        self.assertEquals(4, p1.num_ldas)

        # check num_ldas in p2
        self.assertEquals(2, p2.num_ldas)

        # make sure vmas line up
        self.assertEquals(0x412bec, p1.vma_start)
        self.assertEquals(0x412bf0, p1.vma_end)
        self.assertEquals(0x412bf0, p2.vma_start)
        self.assertEquals(0x412bf5, p2.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(fini_lda_before, parcels_after.vma_to_lda(0x412bec))
        self.assertEquals(True, p2.is_code)

        # these changed
        self.assertEquals(fini_lda_before+1, parcels_after.vma_to_lda(0x412bed))
        self.assertEquals(fini_lda_before+2, parcels_after.vma_to_lda(0x412bee))
        self.assertEquals(fini_lda_before+3, parcels_after.vma_to_lda(0x412bef))
        self.assertEquals(fini_lda_before+4, parcels_after.vma_to_lda(0x412bf0))
        self.assertEquals(fini_lda_before+5, parcels_after.vma_to_lda(0x412bf4))
        self.assertEquals(False, p1.is_code)

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x412bec, parcels_after.lda_to_vma(fini_lda_before))

        # these changed
        self.assertEquals(0x412bed, parcels_after.lda_to_vma(fini_lda_before+1))
        self.assertEquals(0x412bee, parcels_after.lda_to_vma(fini_lda_before+2))
        self.assertEquals(0x412bef, parcels_after.lda_to_vma(fini_lda_before+3))
        self.assertEquals(0x412bf0, parcels_after.lda_to_vma(fini_lda_before+4))
        self.assertEquals(0x412bf4, parcels_after.lda_to_vma(fini_lda_before+5))

    def test_split_to_data_at_end_of_parcel(self):
        odb_file = OdbFile(BinaryFile(self.get_test_bin_path('ls'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))

        # last instruction in .plt
        p = parcels_before.find_parcel_by_vma(0x4029bb)
        p3 = parcels_before.find_parcel_by_vma(0x4029c0)
        num_p1_ldas_before = p.num_ldas
        num_p3_ldas_before = p3.num_ldas
        plt_lda_before = parcels_before.vma_to_lda(0x402320)
        text_lda_before = parcels_before.vma_to_lda(0x4029c0)

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x4029bb))

        # number of parcels after the split (should only add one more)
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(26, len(parcels_after))

        # get the two parcels (plus the .text one following)
        p1 = parcels_after.find_parcel_by_vma(0x402320)
        p2 = parcels_after.find_parcel_by_vma(0x4029bb)
        p3 = parcels_after.find_parcel_by_vma(0x4029c0)

        # make sure they are all unique
        self.assertNotEqual(p1, p2)
        self.assertNotEqual(p1, p3)
        self.assertNotEqual(p2, p3)

        # check num_ldas in p1 (5 instructions)
        self.assertEquals(num_p1_ldas_before - 1, p1.num_ldas)

        # check num_ldas in p2 (this one instruction has now become 5 data bytes)
        self.assertEquals(5, p2.num_ldas)

        # check num_ldas in p3 (should not have changed)
        self.assertEquals(num_p3_ldas_before, p3.num_ldas)

        # make sure vmas line up
        self.assertEquals(0x402320, p1.vma_start)
        self.assertEquals(0x4029bb, p1.vma_end)
        self.assertEquals(0x4029bb, p2.vma_start)
        self.assertEquals(0x4029c0, p2.vma_end)
        self.assertEquals(0x4029c0, p3.vma_start)
        self.assertEquals(0x412bec, p3.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(plt_lda_before, parcels_after.vma_to_lda(0x402320))
        self.assertEquals(plt_lda_before+num_p1_ldas_before-2, parcels_after.vma_to_lda(0x4029b6))
        self.assertEquals(plt_lda_before+num_p1_ldas_before-1, parcels_after.vma_to_lda(0x4029bb))
        self.assertEquals(True, p1.is_code)
        self.assertEquals(True, p3.is_code)

        # these changed
        self.assertEquals(plt_lda_before+num_p1_ldas_before, parcels_after.vma_to_lda(0x4029bc))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+1, parcels_after.vma_to_lda(0x4029bd))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+2, parcels_after.vma_to_lda(0x4029be))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+3, parcels_after.vma_to_lda(0x4029bf))
        self.assertEquals(plt_lda_before+num_p1_ldas_before+4, parcels_after.vma_to_lda(0x4029c0))
        self.assertEquals(False, p2.is_code)

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(text_lda_before+4, parcels_after.vma_to_lda(0x4029c0))

        #
        # make sure lda->vma mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(0x402320, parcels_after.lda_to_vma(plt_lda_before))
        self.assertEquals(0x4029b6, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before-2))
        self.assertEquals(0x4029bb, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before-1))

        # these changed
        self.assertEquals(0x4029bc, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before))
        self.assertEquals(0x4029bd, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before+1))
        self.assertEquals(0x4029be, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before+2))
        self.assertEquals(0x4029bf, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before+3))
        self.assertEquals(0x4029c0, parcels_after.lda_to_vma(plt_lda_before+num_p1_ldas_before+4))

        # 1 instruction turned into 5 data bytes, so it shifted the following parcels by 4 ldas
        self.assertEquals(0x4029c0, parcels_after.lda_to_vma(text_lda_before+4))

    def test_split_to_data_single_inst_in_parcel(self):
        odb_file = OdbFile(BinaryFile(
            self.get_test_bin_path('code_split_single_instruction/split_parcel_single'), 'elf64-x86-64', 'i386:x86-64'))
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        parcels_before = ParcelList(odb_file.get_structure_list(Parcel))

        # only one instruction in .single
        p = parcels_before.find_parcel_by_vma(0x400598)
        p_text = parcels_before.find_parcel_by_vma(0x400597)
        p_fini = parcels_before.find_parcel_by_vma(0x4005a0)
        p_got = parcels_before.find_parcel_by_vma(0x600fe0)
        num_ldas_before = p.num_ldas
        num_text_ldas_before = p_text.num_ldas
        num_fini_ldas_before = p_fini.num_ldas
        single_lda_before = p.lda_start
        fini_lda_before = p_fini.lda_start
        text_lda_before = p_text.lda_start
        got_lda_before = p_got.lda_start

        # number of parcels before the split
        self.assertEquals(25, len(parcels_before))

        # execute the split operation
        odb_file.execute(SplitParcelOperation(0x400598))

        # number of parcels after the split (should not have changed)
        parcels_after = ParcelList(odb_file.get_structure_list(Parcel))
        self.assertEquals(25, len(parcels_after))

        # get the parcels
        p = parcels_after.find_parcel_by_vma(0x400598)
        p_text = parcels_after.find_parcel_by_vma(0x400597)
        p_fini = parcels_after.find_parcel_by_vma(0x4005a0)

        # make sure they are all unique
        self.assertNotEqual(p, p_text)
        self.assertNotEqual(p, p_fini)
        self.assertNotEqual(p_text, p_fini)

        # check num_ldas in p (1 instruction become 7 data bytes)
        self.assertEquals(7, p.num_ldas)

        # check num_ldas in text didn't change
        self.assertEquals(num_text_ldas_before, p_text.num_ldas)

        # check num_ldas in fini didn't change
        self.assertEquals(num_fini_ldas_before, p_fini.num_ldas)

        # make sure vmas line up
        self.assertEquals(0x4003d0, p_text.vma_start)
        self.assertEquals(0x400598, p_text.vma_end)
        self.assertEquals(0x400598, p.vma_start)
        self.assertEquals(0x40059f, p.vma_end)
        self.assertEquals(0x4005a0, p_fini.vma_start)
        self.assertEquals(0x4005ae, p_fini.vma_end)

        #
        # make sure vma->lda mappings line up
        #

        # these shouldn't have changed
        self.assertEquals(text_lda_before, parcels_after.vma_to_lda(0x4003d0))
        self.assertEquals(text_lda_before+num_text_ldas_before-1, parcels_after.vma_to_lda(0x400597))
        self.assertEquals(single_lda_before, parcels_after.vma_to_lda(0x400598))
        self.assertEquals(True, p_text.is_code)
        self.assertEquals(True, p_fini.is_code)

        # these changed
        self.assertEquals(single_lda_before+1, parcels_after.vma_to_lda(0x400599))
        self.assertEquals(single_lda_before+2, parcels_after.vma_to_lda(0x40059a))
        self.assertEquals(single_lda_before+3, parcels_after.vma_to_lda(0x40059b))
        self.assertEquals(single_lda_before+4, parcels_after.vma_to_lda(0x40059c))
        self.assertEquals(single_lda_before+5, parcels_after.vma_to_lda(0x40059d))
        self.assertEquals(single_lda_before+6, parcels_after.vma_to_lda(0x40059e))
        self.assertEquals(False, p.is_code)

        # 1 instruction turned into 7 data bytes, so it shifted the following parcels by 6 ldas
        self.assertEquals(fini_lda_before+6, parcels_after.vma_to_lda(0x4005a0))
        self.assertEquals(got_lda_before+6, parcels_after.vma_to_lda(0x600fe0))

        #
        # make sure lda->vma mappings line up
        #

        self.assertEquals(text_lda_before, parcels_after.vma_to_lda(0x4003d0))
        self.assertEquals(text_lda_before+num_text_ldas_before-1, parcels_after.vma_to_lda(0x400597))
        self.assertEquals(single_lda_before, parcels_after.vma_to_lda(0x400598))

        # these shouldn't have changed
        self.assertEquals(0x4003d0, parcels_after.lda_to_vma(text_lda_before))
        self.assertEquals(0x400597, parcels_after.lda_to_vma(text_lda_before+num_text_ldas_before-1))
        self.assertEquals(0x400598, parcels_after.lda_to_vma(single_lda_before))

        # these changed
        self.assertEquals(0x400599, parcels_after.lda_to_vma(single_lda_before+1))
        self.assertEquals(0x40059a, parcels_after.lda_to_vma(single_lda_before+2))
        self.assertEquals(0x40059b, parcels_after.lda_to_vma(single_lda_before+3))
        self.assertEquals(0x40059c, parcels_after.lda_to_vma(single_lda_before+4))
        self.assertEquals(0x40059d, parcels_after.lda_to_vma(single_lda_before+5))
        self.assertEquals(0x40059e, parcels_after.lda_to_vma(single_lda_before+6))

        # 1 instruction turned into 7 data bytes, so it shifted the following parcels by 6 ldas
        self.assertEquals(0x4005a0, parcels_after.lda_to_vma(fini_lda_before+6))
        self.assertEquals(0x600fe0, parcels_after.lda_to_vma(got_lda_before+6))


    def test_consolidate_data(self):

        # positive, simple case
        p1 = DataParcel(0, 0, 0x1000, '.test')
        p2 = DataParcel(0, 0x1000, 0x2000, '.test')
        p3 = DataParcel(0, 0x2000, 0x3000, '.test')
        parcels = ParcelList([p1, p2, p3])
        transaction = parcels.consolidate()
        self.assertEquals(1, len(parcels))
        self.assertEquals(0, parcels[0].vma_start)
        self.assertEquals(0x3000, parcels[0].vma_end)
        self.assertEquals(0x3000, parcels[0].num_ldas)
        self.assertTrue(p2 in transaction.to_remove)
        self.assertTrue(p3 in transaction.to_remove)

        # positive, but only middle parcels merged
        p1 = DataParcel(0, 0, 0x0fff, '.test')
        p2 = DataParcel(0, 0x1000, 0x2000, '.test')
        p3 = DataParcel(0, 0x2000, 0x3000, '.test')
        p4 = DataParcel(0, 0x3001, 0x4000, '.test')
        parcels = ParcelList([p1, p2, p3, p4])
        transaction = parcels.consolidate()
        self.assertEquals(3, len(parcels))
        self.assertEquals(0, parcels[0].vma_start)
        self.assertEquals(0x1000, parcels[1].vma_start)
        self.assertEquals(0x3001, parcels[2].vma_start)
        self.assertEquals(0x0fff, parcels[0].vma_end)
        self.assertEquals(0x3000, parcels[1].vma_end)
        self.assertEquals(0x4000, parcels[2].vma_end)
        self.assertEquals(0x0fff, parcels[0].num_ldas)
        self.assertEquals(0x2000, parcels[1].num_ldas)
        self.assertEquals(0x0fff, parcels[2].num_ldas)
        self.assertTrue(p3 in transaction.to_remove)
        self.assertEquals(1, len(transaction.to_remove))

        # negative, non-contiguous case
        p1 = DataParcel(0, 0, 0xffff, '.test')
        p2 = DataParcel(0, 0x1000, 0x1fff, '.test')
        p3 = DataParcel(0, 0x2000, 0x3000, '.test')
        parcels = ParcelList([p1, p2, p3])
        transaction = parcels.consolidate()
        self.assertEquals(3, len(parcels))
        self.assertEquals(0, len(transaction.to_remove))
        self.assertTrue(p1 in parcels)
        self.assertTrue(p2 in parcels)
        self.assertTrue(p3 in parcels)

        # negative, disparate types case
        p1 = DataParcel(0, 0, 0x1000, '.test')
        p2 = CodeParcel(0, 0x1000, 0x2000, '.test')
        p3 = DataParcel(0, 0x2000, 0x3000, '.test')
        parcels = ParcelList([p1, p2, p3])
        transaction = parcels.consolidate()
        self.assertEquals(3, len(parcels))
        self.assertEquals(0, len(transaction.to_remove))
        self.assertTrue(p1 in parcels)
        self.assertTrue(p2 in parcels)
        self.assertTrue(p3 in parcels)

        # negative, disparate sections case
        p1 = DataParcel(0, 0, 0x1000, '.test1')
        p2 = CodeParcel(0, 0x1000, 0x2000, '.test2')
        p3 = DataParcel(0, 0x2000, 0x3000, '.test3')
        parcels = ParcelList([p1, p2, p3])
        transaction = parcels.consolidate()
        self.assertEquals(3, len(parcels))
        self.assertEquals(0, len(transaction.to_remove))
        self.assertTrue(p1 in parcels)
        self.assertTrue(p2 in parcels)
        self.assertTrue(p3 in parcels)

    def test_consolidate_code(self):
        # TODO
        pass

