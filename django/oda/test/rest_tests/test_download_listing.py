from rest_framework import status
from oda.test.oda_test_case import OdaApiTestCase


class DownloadListingTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_download_strcpy(self):
        response = self.client.get('/odaweb/_download',
                                   { 'short_name': 'strcpy_x86',
                                     'revision': 0,
                                   },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        listing = response.content
        self.assertIsNotNone(listing)
        lines = listing.decode('utf8').split("\n")
        self.assertEqual(18, len(lines))


