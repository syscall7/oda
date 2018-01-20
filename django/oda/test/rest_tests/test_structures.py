"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class LabelUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_labels(self):
        response = self.client.get('/odaweb/api/labels/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data


class FunctionUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_functions(self):
        response = self.client.get('/odaweb/api/functions/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data

    def test_functions_mkdir(self):
        response = self.client.get('/odaweb/api/functions/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data

class CommentUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_comments(self):
        response = self.client.get('/odaweb/api/comments/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertGreater(len(rd), 0)
        self.assertIsNotNone(rd[0]['comment'])
        self.assertIsNotNone(rd[0]['vma'])


class SectionsTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_sections(self):
        response = self.client.get('/odaweb/api/sections/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEqual(24, len(rd))
        self.assertIsNotNone(rd[0]['flags'])
        self.assertGreater(len(rd[0]['flags']), 0)
        self.assertIsNotNone(rd[0]['name'])
        self.assertIsNotNone(rd[0]['size'])
        self.assertIsNotNone(rd[0]['vma'])


class SymbolsTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_symbols(self):
        response = self.client.get('/odaweb/api/symbols/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEqual(271, len(rd))
        self.assertIsNotNone(rd[0]['name'])
        self.assertIsNotNone(rd[0]['vma'])
        self.assertNotEqual(rd[0]['vma'], 0)
        self.assertIsNotNone(rd[0]['type'])


class StringsTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_strings(self):
        response = self.client.get('/odaweb/api/strings/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEquals(259, len(rd))
        self.assertIsNotNone(rd[0]['addr'])
        self.assertIsNotNone(rd[0]['string'])


class BinaryStringTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_binary_strings(self):
        response = self.client.patch('/odaweb/api/binarystrings/1/', {
            'binary_string': 'ABCD',
            'short_name': 'strcpy_x86',
            'revision': 0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['binary_string'], 'ABCD')



class CStructsTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_cstructs(self):


        response = self.client.get('/odaweb/api/parcels/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Add a struct object
        response = self.client.get('/odaweb/api/cstructs/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEquals(0, len(rd))

        # Check that the struct exists
        response = self.client.post('/odaweb/api/cstructs/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    'name' : 'foo_struct_t',
                                    'is_packed' : True
                                    },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/odaweb/api/cstructs/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEquals(1, len(rd))

        # Add a second struct
        response = self.client.post('/odaweb/api/cstructs/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    'name' : 'bar_struct_t',
                                    'is_packed' : True
                                    },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # Get a list of available fields
        response = self.client.get('/odaweb/api/cstructfieldtypes/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rd = response.data

        self.assertIsNotNone(rd)
        self.assertEquals(12, len(rd))

        #str(rd[0]['object_id'])

        response = self.client.get('/odaweb/api/cstructs/'+ '0' + '/modify/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    'field_types[]' : [ 'uint16_t',
                                                        'bar_struct_t'],
                                    'field_names[]' : [ 'my_field1', 'my_field3'],
                                    },
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/odaweb/api/cstructs/'+ '1' + '/modify/',
                                   {'revision': 0,
                                    'short_name': 'mkdir',
                                    'field_types[]' : [ 'uint16_t'],
                                    'field_names[]' : [ 'my_field3'],
                                    },
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        #
        # # Add a built-in type field
        # response = self.client.get('/odaweb/api/cstructs/'+ '0' + '/append_field/',
        #                            {'revision': 0,
        #                             'short_name': 'mkdir',
        #                             'field_type' : 'uint16_t',
        #                             'field_name' : 'my_field'},
        #                            format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        #
        # # Add a built-in type field
        # response = self.client.get('/odaweb/api/cstructs/'+ '1' + '/append_field/',
        #                            {'revision': 0,
        #                             'short_name': 'mkdir',
        #                             'field_type' : 'uint16_t',
        #                             'field_name' : 'my_inner_field'},
        #                            format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        #
        #
        # # Add a field that is another struct
        # response = self.client.get('/odaweb/api/cstructs/'+ '0' + '/append_field/',
        #                            {'revision': 0,
        #                             'short_name': 'mkdir',
        #                             'field_type' : 'bar_struct_t',
        #                             'field_name' : 'my_field3'},
        #                            format='json')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)


        # Add a structure object
        response = self.client.get('/odaweb/api/definedData/',
                           { 'revision': 0,
                             'short_name': 'mkdir',
                             'vma': 0x400238,
                             'type_kind': 'struct',
                             'type_name': 'foo_struct_t',
                             'var_name' : 'fooObj',},
                           format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # before the split
        after_struct_add = (
            ('',     0x4014d9, '.init', 'e8'),
            ('',     0x4014da, '.init', '12'),
            ('',     0x4014db, '.init', '05'),
            ('',     0x4014dc, '.init', '00'),
            ('',     0x4014dd, '.init', '00'),
        )

        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '0x400238',
                                     'units' : len(after_struct_add)},
                                   format='json')

        # for expected, actual in zip(after_struct_add, rd):
        #     self.assertEquals(expected[0], actual['opcode'])
        #     self.assertEquals(expected[1], actual['vma'])
        #     self.assertEquals(expected[2], actual['section_name'])
        #     self.assertEquals(expected[3], actual['rawBytes'])
        #
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/odaweb/api/parcels/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
