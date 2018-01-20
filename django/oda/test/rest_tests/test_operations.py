from rest_framework import status
from oda.test.oda_test_case import OdaApiTestCase


class OperationsViewTest(OdaApiTestCase):
    urls = 'oda.urls'

    def helper_fetch_operations(self, shortname):
        response = self.client.get('/odaweb/api/operations/',
                                   { 'short_name': shortname,
                                     'revision': 0},
                                   format='json')
        return response

    def test_operations_exist(self):

        response = self.helper_fetch_operations('mkdir')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operations = response.data
        self.assertIsNotNone(operations)

    def test_operations_comment(self):

        shortname = 'mkdir'

        # make a comment
        response = self.client.post('/odaweb/api/comments/',
                                    {'revision': 0,
                                     'short_name': shortname,
                                     'vma': 0x400254,
                                     'comment': "some comment"},
                                    format='json')
        self.assertIs(response.status_code, status.HTTP_200_OK)

        response = self.helper_fetch_operations(shortname)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operations = response.data
        self.assertIsNotNone(operations)

        self.assertEqual(operations[-1]['name'], 'CreateCommentOperation')

    def test_operations_function(self):

        shortname = 'mkdir'

        # create a function
        response = self.client.post('/odaweb/api/displayunits/1/makeFunction/',
                                    {'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': 4200833,
                                     'name': 'some_func',
                                     'args': 'uint8_t a, uint16_t b',
                                     'retval': 'uint32_t'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.helper_fetch_operations(shortname)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operations = response.data
        self.assertIsNotNone(operations)

        self.assertEqual(operations[-1]['name'], 'CreateFunctionOperation')
