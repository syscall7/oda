from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class DisplayUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_display_units(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'strcpy_x86'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEqual(17, len(rd))
        self.assertEqual('.data', rd[0]['section_name'])
        self.assertEqual('55', rd[0]['rawBytes'])
        self.assertEqual(False, rd[0]['isBranch'])
        self.assertEqual(False, rd[0]['isFunction'])
        self.assertEqual(0, rd[0]['vma'])
        self.assertEqual('ebp', rd[0]['operands'])

    def test_display_units_by_vma(self):

        expect = (
            ('.init', True,  False, 0x004014d0, '4883ec08',     'sub',  'rsp,0x8'),
            ('.init', False, False, 0x004014d4, 'e883040000',   'call', '0x0040195c'),
            ('.init', False, False, 0x004014d9, 'e812050000',   'call', '0x004019f0'),
            ('.init', False, False, 0x004014de, 'e87db10000',   'call', '0x0040c660'),
            ('.init', False, False, 0x004014e3, '4883c408',	    'add',  'rsp,0x8'),
            ('.init', False, False, 0x004014e7, 'c3',	        'ret',  ''),
            ('.plt',  True,  False, 0x004014f0, 'ff35faea2000', 'push', 'QWORD PTR [rip+0x20eafa]        # 0x0060fff0'),
            ('.plt',  False, False, 0x004014f6,  'ff25fcea2000','jmp',  'QWORD PTR [rip+0x20eafc]        # 0x0060fff8'),
            ('.plt',  False, False, 0x004014fc, '0f1f4000',	    'nop',  'DWORD PTR [rax+0x0]'),
        )

        tests = (
            (0x4014d0, len(expect)),    # go forward
            (0x4014FC, -len(expect)),   # and backward
        )

        for vma, lines in tests:

            response = self.client.get('/odaweb/api/displayunits/', {
                            'revision': 0,
                            'short_name': 'mkdir',
                            'addr' : vma,
                            'units' : lines,
                        }, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            rd = response.data
            self.assertIsNotNone(rd)
            self.assertEqual(len(expect), len(rd))

            for expected, actual in zip(expect, rd):
                msg = None # 'at address 0x%08x' % actual['vma']
                self.assertEqual(expected[0], actual['section_name'], msg)
                self.assertEqual(expected[1], actual['isFunction'], msg)
                self.assertEqual(expected[2], actual['isBranch'], msg)
                self.assertEqual(expected[3], actual['vma'], msg)
                self.assertEqual(expected[4], actual['rawBytes'], msg)
                self.assertEqual(expected[5], actual['opcode'], msg)
                self.assertEqual(expected[6], actual['operands'].strip(), msg)
                self.assertEqual(True, actual['isCode'], msg)
                # actual['instStr']

    def test_display_units_mkdir_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir', 'addr' : '0x4014d0'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['vma'], 0x4014d0)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], True)
        self.assertEquals(rd[0]['section_name'], '.init')
        self.assertEquals(rd[0]['instStr'], 'sub    rsp,0x8')

    def test_display_units_mkdir_data(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   {'revision': 0, 'short_name': 'mkdir', 'addr' : '0x400238'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], '')
        self.assertEquals(rd[0]['operands'], '')
        self.assertEquals(rd[0]['rawBytes'], '2f')
        self.assertEquals(rd[0]['vma'], 0x400238)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], False)
        self.assertEquals(rd[0]['section_name'], '.interp')
        self.assertEquals(rd[0]['instStr'], "<insn>db</insn>  <span class='raw'>2fh</span> <span class='comment'>; /</span>")

    def test_display_units_mkdir_logical_data_and_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '10',
                                     'units' : '4743',
                                     'logical' : 'true'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)

        self.assertEquals(rd[0]['opcode'], '')
        self.assertEquals(rd[0]['operands'], '')
        self.assertEquals(rd[0]['rawBytes'], '6c')
        self.assertEquals(rd[0]['vma'], 0x400242)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], False)
        self.assertEquals(rd[0]['section_name'], '.interp')
        self.assertEquals(rd[0]['instStr'], "<insn>db</insn>  <span class='raw'>6ch</span> <span class='comment'>; l</span>")

        # next data section
        self.assertEquals(rd[18]['opcode'], '')
        self.assertEquals(rd[18]['operands'], '')
        self.assertEquals(rd[18]['rawBytes'], '04')
        self.assertEquals(rd[18]['vma'], 0x400254)
        self.assertEquals(rd[18]['isBranch'], False)
        self.assertEquals(rd[18]['isFunction'], False)
        self.assertEquals(rd[18]['section_name'], '.note.ABI-tag')
        self.assertEquals(rd[18]['instStr'], "<insn>db</insn>  <span class='raw'>04h</span>")

        # the last entry should be the first instruction of the first code section
        self.assertEquals(rd[-1]['opcode'], 'sub')
        self.assertEquals(rd[-1]['operands'], 'rsp,0x8')
        self.assertEquals(rd[-1]['rawBytes'], '4883ec08')
        self.assertEquals(rd[-1]['vma'], 0x4014d0)
        self.assertEquals(rd[-1]['isBranch'], False)
        self.assertEquals(rd[-1]['isFunction'], True)
        self.assertEquals(rd[-1]['section_name'], '.init')
        self.assertEquals(rd[-1]['instStr'], 'sub    rsp,0x8')

    def test_display_units_mkdir_logical_code(self):
        response = self.client.get('/odaweb/api/displayunits/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir',
                                     'addr' : '4752',
                                     'units' : '100',
                                     'logical' : 'true'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEquals(len(rd), 100)

        # first instruction of first code section
        self.assertEquals(rd[0]['opcode'], 'sub')
        self.assertEquals(rd[0]['operands'], 'rsp,0x8')
        self.assertEquals(rd[0]['rawBytes'], '4883ec08')
        self.assertEquals(rd[0]['vma'], 0x4014d0)
        self.assertEquals(rd[0]['isBranch'], False)
        self.assertEquals(rd[0]['isFunction'], True)
        self.assertEquals(rd[0]['section_name'], '.init')
        self.assertEquals(rd[0]['instStr'], 'sub    rsp,0x8')

        # first instruction of next code section
        self.assertEquals(rd[6]['opcode'], 'push')
        self.assertEquals(rd[6]['operands'], 'QWORD PTR [rip+0x20eafa]        # 0x0060fff0')
        self.assertEquals(rd[6]['rawBytes'], 'ff35faea2000')
        self.assertEquals(rd[6]['vma'], 0x4014f0)
        self.assertEquals(rd[6]['isBranch'], False)
        self.assertEquals(rd[6]['isFunction'], True)
        self.assertEquals(rd[6]['section_name'], '.plt')
        self.assertEquals(rd[6]['instStr'], 'push   QWORD PTR [rip+0x20eafa]        # 0x0060fff0')

    def test_display_units_mkdir_size(self):
        response = self.client.get('/odaweb/api/displayunits/1/size/',
                                   { 'revision': 0,
                                     'short_name': 'mkdir'},
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rd = response.data
        self.assertIsNotNone(rd)
        self.assertEquals(rd, 28439)

    def test_display_units_mkdir_vma_to_lda(self):

        tests = (
            (0x400238, 0),      # first data byte (in .interp)
            (0x4014d0, 4752),   # first instruction of executable (in .init)
            (0x6102b7, 28438),      # last data byte of executable (in .data)
            (0x6102b8, None)    # one byte beyond executable image
        )

        for vma, expected_lda in tests:
            response = self.client.get('/odaweb/api/displayunits/1/vmaToLda/',
                                       { 'revision': 0,
                                         'short_name': 'mkdir',
                                         'vma': vma},
                                       format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            actual_lda = response.data
            self.assertEquals(expected_lda, actual_lda)

    def test_display_units_mkdir_lda_to_vma(self):

        tests = (
            (0x400238, 0),      # first data byte (in .interp)
            (0x4014d0, 4752),   # first instruction of executable (in .init)
            (0x6102b7, 28438),  # last data byte of executable (in .data)
            (None, 28439)       # one lda beyond executable image
        )

        for expected_vma, lda in tests:
            response = self.client.get('/odaweb/api/displayunits/1/ldaToVma/',
                                       { 'revision': 0,
                                         'short_name': 'mkdir',
                                         'lda': lda},
                                       format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            actual_vma = response.data
            self.assertEquals(expected_vma, actual_vma)

    def test_display_units_sorted_xrefs(self):

            # get the list of functions for the mkdir program
            response = self.client.get('/odaweb/api/functions/',
                               {'revision': 0, 'short_name': 'mkdir'},
                               format='json')

            functions = response.data

            # for each function in the list
            for f in functions:
                print(f)
                # request the display unit at the function address
                response = self.client.get('/odaweb/api/displayunits/', {
                                'revision': 0,
                                'short_name': 'mkdir',
                                'addr' : f['vma'],
                                'units' : 1,
                            }, format='json')
                du = response.data[0]

                # verify that the cross references for this du are sorted
                # TODO: What?
                #for idx, crossRef in enumerate(du['crossRef']):
                #    self.assertEqual(crossRef, sorted(du['crossRef'][idx]))

                #du['crossRef'] == sorted(du['crossRef'])
                #self.assertEqual()


