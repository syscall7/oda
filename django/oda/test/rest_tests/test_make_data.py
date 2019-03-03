from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class MakeDataUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_make_data_on_data(self):
        # make data on data, should fail
        response = self.client.get('/odaapi/api/displayunits/1/makeData/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4002cd},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # this should fail
        self.assertNotEqual(response.data['error'], None)

    def test_simple_make_data(self):

        # before the split
        before_split = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('call', 0x4014d9, '.init', 'e812050000'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt',  'ff35faea2000'),
        )

        # after the split
        after_split = (
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

        # after the split
        after_double_data = (
            ('sub',  0x4014d0, '.init', '4883ec08'),
            ('call', 0x4014d4, '.init', 'e883040000'),
            ('',     0x4014d9, '.init', 'e8'),
            ('',     0x4014da, '.init', '0512'),
            ('',     0x4014dc, '.init', '00'),
            ('',     0x4014dd, '.init', '00'),
            ('call', 0x4014de, '.init', 'e87db10000'),
            ('add',  0x4014e3, '.init', '4883c408'),
            ('ret',  0x4014e7, '.init', 'c3'),
            ('push', 0x4014f0, '.plt',  'ff35faea2000'),
        )

        response = self.client.get('/odaapi/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : len(before_split)},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        for expected, actual in zip(before_split, rd):
            self.assertEqual(expected[0], actual['opcode'])
            self.assertEqual(expected[1], actual['vma'])
            self.assertEqual(expected[2], actual['section_name'])
            self.assertEqual(expected[3], actual['rawBytes'])

        response = self.client.get('/odaapi/api/displayunits/1/makeData/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 0x4014d9},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/odaapi/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x004014d0',
                                     'units' : len(after_split)},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        for expected, actual in zip(after_split, rd):
            isCode = expected[0] != ''
            self.assertEqual(expected[0], actual['opcode'])
            self.assertEqual(expected[1], actual['vma'])
            self.assertEqual(expected[2], actual['section_name'])
            self.assertEqual(expected[3], actual['rawBytes'])
            self.assertEqual(isCode, actual['isCode'])

