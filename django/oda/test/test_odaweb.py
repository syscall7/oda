"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os

from oda.test.oda_test_case import OdaApiTestCase

cwd = os.path.dirname(os.path.realpath(__file__))

class IndexTest(OdaApiTestCase):
    def test_index(self):
        response = self.client.get('/odaweb/')

        self.assertEqual(response.status_code, 200)

        self.assertTrue('master' in response.context)
        self.assertTrue('examples' in response.context)

    def test_mkdir(self):
        response = self.client.get('/odaweb/mkdir')

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['binary'].name, 'mkdir')

    def test_upload_elf(self):
        f = open(os.path.join(cwd, '../apps/odaweb/examples/mkdir'), 'rb')
        response = self.client.post('/odaweb/_upload', {
            'project_name': 'test',
            'default_sharing_level': 'read',
            'filedata': f
        })
        f.close()

        self.assertEqual(response.status_code, 200)

    def test_rando_binary(self):
        with open(os.path.join(cwd, '../apps/odaweb/examples/ls.bin.x86-64'), 'rb') as fp:
            response = self.client.post('/odaweb/_upload', {
                'project_name': 'test',
                'default_sharing_level': 'read',
                'filedata': fp
            })

            self.assertEqual(response.status_code, 200)



    #def test_set(self):
    #    response = self.client.patch('/odaweb/_set', {
    #        'arch': 'i386:x86-64:intel',
    #        'base_address': '0'
    #    })
    #
    #    self.assertEqual(response.status_code, 200)
