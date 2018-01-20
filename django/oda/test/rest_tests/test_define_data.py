"""
This file contains tests for defining data in data sections.
"""

from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class DefineDataTests(OdaApiTestCase):
    urls = 'oda.urls'

    def test_simple_ascii_string(self):

        # create an ascii string
        response = self.client.post('/odaweb/api/definedData/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    'type_kind' : 'builtin',
                                    'type_name' : 'ascii',
                                    'var_name'  : 'mystr',
                                    'vma'       : 0x400260
                                    },
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dd = response.data['definedData']

        # verify data was defined
        response = self.client.get('/odaweb/api/definedData/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    },
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_dd = response.data
        self.assertEqual(1, len(returned_dd))

        # verify data
        for definedData in [returned_dd[0], response_dd]:
            self.assertIsNotNone(definedData)
            self.assertEqual(definedData['type_kind'], 'builtin')
            self.assertEqual(definedData['type_name'], 'ascii')
            self.assertEqual(definedData['var_name'], 'mystr')
            self.assertEqual(definedData['vma'], 0x400260)
            self.assertEqual(definedData['size'], 4)



        after_define_data = (
            ('',     0x400260, '.note.ABI-tag', '474e5500'),
        )

        # verify data is displayed correctly
        response = self.client.get('/odaweb/api/displayunits/',
                           { 'revision': 0,
                             'short_name': 'mkdir',
                             'addr' : '0x400260',
                             'units' : len(after_define_data)},
                           format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for expected, actual in zip(after_define_data, response.data):
            self.assertEquals(expected[0], actual['opcode'])
            self.assertEquals(expected[1], actual['vma'])
            self.assertEquals(expected[2], actual['section_name'])
            self.assertEquals(expected[3], actual['rawBytes'])

    def test_merge_ascii_string(self):
        # TODO: Verify we can merge adjacent strings
        pass

    def test_undefine_string(self):
        # create an ascii string
        response = self.client.post('/odaweb/api/definedData/',
                                    {'revision': 0,
                                     'short_name': 'mkdir',
                                     'type_kind' : 'builtin',
                                     'type_name' : 'ascii',
                                     'var_name'  : 'mystr',
                                     'vma'       : 0x400260
                                     },
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify data was defined
        response = self.client.get('/odaweb/api/definedData/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    },
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_dd = response.data
        self.assertEqual(1, len(returned_dd))

        # undefine the data
        response = self.client.delete('/odaweb/api/definedData/0/',
                                    {'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma'       : 0x400260
                                     },
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # verify data was undefined
        response = self.client.get('/odaweb/api/definedData/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    },
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_dd = response.data
        self.assertEqual(0, len(returned_dd))
