from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class GraphViewTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_graph_view_binary_string(self):
        response = self.client.get('/odaweb/api/graph',
                                   { 'short_name': 'strcpy_x86',
                                     'revision': 0,
                                     'addr': 0 },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        graphInfo = response.data
        self.assertIsNotNone(graphInfo)
        self.assertIn('nodes', graphInfo)
        self.assertIn('links', graphInfo)

        # verify nodes are as expected
        expected = [
            { 'id': '0x0', 'opcodes': ['push', 'xor', 'mov', 'mov', 'push', 'mov', 'push', 'lea']},
            { 'id': '0x10', 'opcodes': ['movzx', 'mov', 'add', 'test', 'jne']},
            { 'id': '0x1f', 'opcodes': ['pop', 'pop', 'pop', 'ret']},
        ]
        nodes = graphInfo['nodes']
        self.assertEqual(len(nodes), len(expected))
        for n, e in zip(sorted(nodes, key=lambda n: n['id']), sorted(expected, key=lambda n: n['id'])):
            self.assertEqual(n['id'], e['id'])
            self.assertEqual(len(n['instructions']), len(e['opcodes']))
            for ni, ei in zip(n['instructions'], e['opcodes']):
                # don't bother testing all the fields in the display unit, just the opcode
                self.assertEqual(ni['opcode'], ei)

        # verify links are as expected
        expected = [
            {'from': '0x0', 'to': '0x10', 'type': 'unconditional'},
            {'from': '0x10', 'to': '0x10', 'type': 'taken'},
            {'from': '0x10', 'to': '0x1f', 'type': 'notTaken'},
        ]
        links = graphInfo['links']
        self.assertCountEqual(links, expected)

        print('done')

    def test_graph_view_binary_string_nonzero_base_address(self):
        pass

    # test the "open_safer" function in mkdir at 0x405cb4
    def test_mkdir_open_safer(self):
        response = self.client.get('/odaweb/api/graph',
                                   { 'short_name': 'mkdir',
                                     'revision': 0,
                                     'addr': 0x405cb4 },
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        graphInfo = response.data
        self.assertIsNotNone(graphInfo)
        self.assertIn('nodes', graphInfo)
        self.assertIn('links', graphInfo)

        # verify nodes are as expected
        expected = [
            { 'id': '0x405cb4', 'len': 10},
            { 'id': '0x405ce6', 'len': 8},
            { 'id': '0x405d06', 'len': 6},
            { 'id': '0x405d23', 'len': 9},
            { 'id': '0x405d5b', 'len': 8},
            { 'id': '0x405d7e', 'len': 4},
            { 'id': '0x405d93', 'len': 2},
            { 'id': '0x405d9b', 'len': 13},
        ]
        nodes = graphInfo['nodes']
        self.assertEqual(len(nodes), len(expected))
        nodes.sort(key=lambda x: x['id'])
        expected.sort(key=lambda x: x['id'])
        for n, e in zip(nodes, expected):
            self.assertEqual(n['id'], e['id'])
            self.assertEqual(len(n['instructions']), e['len'])

        # verify links are as expected
        #expected = [
        #    {'from': '0x0', 'to': '0x10', 'type': 'unconditional'},
        #    {'from': '0x10', 'to': '0x10', 'type': 'taken'},
        #    {'from': '0x10', 'to': '0x1f', 'type': 'notTaken'},
        #]
        #links = graphInfo['links']
        #self.assertItemsEqual(links, expected)

        print('done')
