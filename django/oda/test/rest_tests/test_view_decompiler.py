from rest_framework import status
from oda.test.oda_test_case import OdaApiTestCase


class DecompilerViewTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_decompiler_view_binary_string(self):
        response = self.client.get('/odaweb/api/decompiler',
                                   { 'short_name': 'strcpy_x86',
                                     'revision': 0,
                                     'addr': 0 },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        decompilerInfo = response.data
        self.assertIsNotNone(decompilerInfo)

        self.assertIn('start', decompilerInfo)
        self.assertEqual(0, decompilerInfo['start'])
        self.assertIn('end', decompilerInfo)
        self.assertEqual(34, decompilerInfo['end'])
        self.assertIn('source', decompilerInfo)
        self.assertNotEqual('', decompilerInfo['source'])

    def test_decompiler_view_binary_string_addr_nonexistent(self):
        response = self.client.get('/odaweb/api/decompiler',
                                   { 'short_name': 'strcpy_x86',
                                     'revision': 0,
                                     'addr': 0xffffffff },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # test the "open_safer" function in mkdir at 0x405cb4
    def test_decompiler_view_mkdir_open_safer(self):
        response = self.client.get('/odaweb/api/decompiler',
                                   { 'short_name': 'mkdir',
                                     'revision': 0,
                                     'addr': 0x405cb4 },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        decompilerInfo = response.data
        self.assertIsNotNone(decompilerInfo)
        self.assertIn('start', decompilerInfo)
        self.assertEqual(0x405cb4, decompilerInfo['start'])
        self.assertIn('end', decompilerInfo)
        self.assertEqual(0x405dc8, decompilerInfo['end'])
        self.assertIn('source', decompilerInfo)
        self.assertNotEqual('', decompilerInfo['source'])

    def test_decompiler_view_mkdir_addr_nonexistent(self):
        response = self.client.get('/odaweb/api/decompiler',
                                   { 'short_name': 'mkdir',
                                     'revision': 0,
                                     'addr': 0xffffffff },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
