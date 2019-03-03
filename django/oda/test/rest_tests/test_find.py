from rest_framework import status
from oda.test.oda_test_case import OdaApiTestCase


class FindTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_find_str(self):
        response = self.client.get('/odaapi/api/find/',
                                   { 'short_name': 'mkdir',
                                     'revision': 0,
                                     'bytes': '"GNU"',
                                   },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = (
            (4194912, '.note.ABI-tag'),
            (4194944, '.note.gnu.build-id'),
            (4245399, '.rodata'),
            (4245435, '.rodata'),
            (4248777, '.rodata'),
            (4249543, '.rodata'),
            (4249579, '.rodata'),
        )

        actual = response.data
        self.assertIsNotNone(actual)
        self.assertEqual(len(expected), len(actual))

        for (e, a) in zip(expected, actual):
            self.assertEqual(e[0], int(a['addr']))
            self.assertEqual(e[1], a['section'])


