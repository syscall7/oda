from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class MakeCodeUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_size(self):

        def get_size():
            response = self.client.get('/odaapi/api/displayunits/1/size/',
                                       { 'revision': 0,
                                         'short_name': 'strcpy_x86'},
                                       format='json')
            return response.data

        # verify initial size
        self.assertEqual(17, get_size())

        # make data at fourth instruction
        response = self.client.get('/odaapi/api/displayunits/1/makeData/',
                                   { 'revision': 0,
                                     'short_name': 'strcpy_x86',
                                     'vma': 5},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # verify size
        self.assertEqual(19, get_size())

        # convert back to code
        response = self.client.get('/odaapi/api/displayunits/1/makeCode/',
                                   { 'revision': 0,
                                     'short_name': 'strcpy_x86',
                                     'vma': 5},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # verify size
        self.assertEqual(17, get_size())

    def test_make_bad_code(self):

        # attempt to make code at an address with an invalid opcode
        response = self.client.get('/odaapi/api/displayunits/1/makeCode/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4002cd},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # we *should* get an error message
        print(response.data)
        self.assertNotEqual(response.data['detail'], None)

    def test_make_code_on_code(self):
        # attempt to make code at an address that is already code
        response = self.client.get('/odaapi/api/displayunits/1/makeCode/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4002cd},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # we *should* get an error message
        self.assertNotEqual(response.data['detail'], None)

    def test_simple_make_code(self):

        # before making_data
        inst_before = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('call', 0x4014d9, '.init', 'e812050000'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt',  'ff35faea2000'),
        )

        # after making data
        inst_after = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('',     0x4014d9, '.init', 'e8'),
            ('',     0x4014da, '.init', '12'),
            ('',     0x4014db, '.init', '05'),
            ('',     0x4014dc, '.init', '00'),
            ('',     0x4014dd, '.init', '00'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt',  'ff35faea2000'),
        )

        # parcels before making data
        parcels_before = (
            {'vma_start': 0x00400238, 'vma_end': 0x00400254, 'lda_start': 0x00000000, 'is_code': False,},
            {'vma_start': 0x00400254, 'vma_end': 0x00400274, 'lda_start': 0x0000001c, 'is_code': False,},
            {'vma_start': 0x00400274, 'vma_end': 0x00400298, 'lda_start': 0x0000003c, 'is_code': False,},
            {'vma_start': 0x00400298, 'vma_end': 0x004002dc, 'lda_start': 0x00000060, 'is_code': False,},
            {'vma_start': 0x004002e0, 'vma_end': 0x00400a18, 'lda_start': 0x000000a4, 'is_code': False,},
            {'vma_start': 0x00400a18, 'vma_end': 0x00400cf2, 'lda_start': 0x000007dc, 'is_code': False,},
            {'vma_start': 0x00400cf2, 'vma_end': 0x00400d8c, 'lda_start': 0x00000ab6, 'is_code': False,},
            {'vma_start': 0x00400d90, 'vma_end': 0x00400de0, 'lda_start': 0x00000b50, 'is_code': False,},
            {'vma_start': 0x00400de0, 'vma_end': 0x00400e88, 'lda_start': 0x00000ba0, 'is_code': False,},
            {'vma_start': 0x00400e88, 'vma_end': 0x004014d0, 'lda_start': 0x00000c48, 'is_code': False,},
            {'vma_start': 0x004014d0, 'vma_end': 0x004014e8, 'lda_start': 0x00001290, 'is_code': True,},
            {'vma_start': 0x004014f0, 'vma_end': 0x00401930, 'lda_start': 0x00001296, 'is_code': True,},
            {'vma_start': 0x00401930, 'vma_end': 0x0040c698, 'lda_start': 0x00001362, 'is_code': True,},
            {'vma_start': 0x0040c698, 'vma_end': 0x0040c6a6, 'lda_start': 0x00003d7b, 'is_code': True,},
            {'vma_start': 0x0040c6c0, 'vma_end': 0x0040dce0, 'lda_start': 0x00003d7f, 'is_code': False,},
            {'vma_start': 0x0040dce0, 'vma_end': 0x0040e164, 'lda_start': 0x0000539f, 'is_code': False,},
            {'vma_start': 0x0040e168, 'vma_end': 0x0040f3cc, 'lda_start': 0x00005823, 'is_code': False,},
            {'vma_start': 0x0060fe20, 'vma_end': 0x0060fe30, 'lda_start': 0x00006a87, 'is_code': False,},
            {'vma_start': 0x0060fe30, 'vma_end': 0x0060fe40, 'lda_start': 0x00006a97, 'is_code': False,},
            {'vma_start': 0x0060fe40, 'vma_end': 0x0060fe48, 'lda_start': 0x00006aa7, 'is_code': False,},
            {'vma_start': 0x0060fe48, 'vma_end': 0x0060ffd8, 'lda_start': 0x00006aaf, 'is_code': False,},
            {'vma_start': 0x0060ffd8, 'vma_end': 0x0060ffe8, 'lda_start': 0x00006c3f, 'is_code': False,},
            {'vma_start': 0x0060ffe8, 'vma_end': 0x00610218, 'lda_start': 0x00006c4f, 'is_code': False,},
            {'vma_start': 0x00610220, 'vma_end': 0x006102b8, 'lda_start': 0x00006e7f, 'is_code': False,}
        )

        # parcels after making data
        parcels_after = (
            {'vma_start': 0x00400238, 'vma_end': 0x00400254, 'lda_start': 0x00000000, 'is_code': False,},
            {'vma_start': 0x00400254, 'vma_end': 0x00400274, 'lda_start': 0x0000001c, 'is_code': False,},
            {'vma_start': 0x00400274, 'vma_end': 0x00400298, 'lda_start': 0x0000003c, 'is_code': False,},
            {'vma_start': 0x00400298, 'vma_end': 0x004002dc, 'lda_start': 0x00000060, 'is_code': False,},
            {'vma_start': 0x004002e0, 'vma_end': 0x00400a18, 'lda_start': 0x000000a4, 'is_code': False,},
            {'vma_start': 0x00400a18, 'vma_end': 0x00400cf2, 'lda_start': 0x000007dc, 'is_code': False,},
            {'vma_start': 0x00400cf2, 'vma_end': 0x00400d8c, 'lda_start': 0x00000ab6, 'is_code': False,},
            {'vma_start': 0x00400d90, 'vma_end': 0x00400de0, 'lda_start': 0x00000b50, 'is_code': False,},
            {'vma_start': 0x00400de0, 'vma_end': 0x00400e88, 'lda_start': 0x00000ba0, 'is_code': False,},
            {'vma_start': 0x00400e88, 'vma_end': 0x004014d0, 'lda_start': 0x00000c48, 'is_code': False,},

            # this is where the new data parcel was created
            {'vma_start': 0x004014d0, 'vma_end': 0x004014d9, 'lda_start': 0x00001290, 'is_code': True,},
            {'vma_start': 0x004014d9, 'vma_end': 0x004014de, 'lda_start': 0x00001292, 'is_code': False,},
            {'vma_start': 0x004014de, 'vma_end': 0x004014e8, 'lda_start': 0x00001297, 'is_code': True,},

            # lda_start is bumped up for all these parcels due to the new data parcel
            {'vma_start': 0x004014f0, 'vma_end': 0x00401930, 'lda_start': 0x0000129a, 'is_code': True,},
            {'vma_start': 0x00401930, 'vma_end': 0x0040c698, 'lda_start': 0x00001366, 'is_code': True,},
            {'vma_start': 0x0040c698, 'vma_end': 0x0040c6a6, 'lda_start': 0x00003d7f, 'is_code': True,},
            {'vma_start': 0x0040c6c0, 'vma_end': 0x0040dce0, 'lda_start': 0x00003d83, 'is_code': False,},
            {'vma_start': 0x0040dce0, 'vma_end': 0x0040e164, 'lda_start': 0x000053a3, 'is_code': False,},
            {'vma_start': 0x0040e168, 'vma_end': 0x0040f3cc, 'lda_start': 0x00005827, 'is_code': False,},
            {'vma_start': 0x0060fe20, 'vma_end': 0x0060fe30, 'lda_start': 0x00006a8b, 'is_code': False,},
            {'vma_start': 0x0060fe30, 'vma_end': 0x0060fe40, 'lda_start': 0x00006a9b, 'is_code': False,},
            {'vma_start': 0x0060fe40, 'vma_end': 0x0060fe48, 'lda_start': 0x00006aab, 'is_code': False,},
            {'vma_start': 0x0060fe48, 'vma_end': 0x0060ffd8, 'lda_start': 0x00006ab3, 'is_code': False,},
            {'vma_start': 0x0060ffd8, 'vma_end': 0x0060ffe8, 'lda_start': 0x00006c43, 'is_code': False,},
            {'vma_start': 0x0060ffe8, 'vma_end': 0x00610218, 'lda_start': 0x00006c53, 'is_code': False,},
            {'vma_start': 0x00610220, 'vma_end': 0x006102b8, 'lda_start': 0x00006e83, 'is_code': False,}
        )

        def get_and_verify_display_units(vma, expected_instrs):

            # get the display units
            response = self.client.get('/odaapi/api/displayunits/',
                                       { 'revision': 0,
                                         'short_name': 'mkdir',
                                         'addr' : '0x004014d0',
                                         'units' : len(inst_before)},
                                       format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            rd = response.data
            self.assertIsNotNone(rd)

            # verify they are what we expect
            for expected, actual in zip(expected_instrs, rd):
                isCode = expected[0] != ''
                self.assertEqual(expected[0], actual['opcode'])
                self.assertEqual(expected[1], actual['vma'])
                self.assertEqual(expected[2], actual['section_name'])
                self.assertEqual(expected[3], actual['rawBytes'])
                self.assertEqual(isCode, actual['isCode'])



        def get_and_verify_parcels(expected_parcels):
            # get the parcels before converting to code
            response = self.client.get('/odaapi/api/parcels/',
                                       { 'revision': 0,
                                         'short_name': 'mkdir'},
                                       format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            rd = response.data
            self.assertIsNotNone(rd)

            # verify they are what we expect (original code)
            for expected, actual in zip(expected_parcels, rd):
                self.assertEqual(expected, actual)


        # verify the display units and parcels before making data
        get_and_verify_display_units(0x4014d0, inst_before)
        get_and_verify_parcels(parcels_before)

        # convert the second call instruction to data bytes
        response = self.client.get('/odaapi/api/displayunits/1/makeData/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4014d9},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # verify the display units and parcels AFTER making data
        get_and_verify_display_units(0x4014d0, inst_after)
        get_and_verify_parcels(parcels_after)

        # convert the data back to code
        response = self.client.get('/odaapi/api/displayunits/1/makeCode/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4014d9},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # verify the display units and parcels are back to where we started
        get_and_verify_display_units(0x4014d0, inst_before)
        get_and_verify_parcels(parcels_before)

