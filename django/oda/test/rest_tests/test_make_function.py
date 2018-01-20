from rest_framework import status

from oda.test.oda_test_case import OdaApiTestCase


class MakeFunctionUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_simple_make_function(self):
        # the year I was born...well, kinda
        #FUNC_ADDR = 0x401981
        FUNC_ADDR = 4200833
        FUNC_NAME = 'birthday_func'
        FUNC_ARGS = 'uint8_t,uint16_t'
        FUNC_RETVAL = 'uint32_t'

        # create a function
        response = self.client.post('/odaweb/api/displayunits/1/makeFunction/',
                                    {'revision': 0,
                                     'short_name': 'mkdir',
                                     'vma': FUNC_ADDR,
                                     'name': FUNC_NAME,
                                     'args': FUNC_ARGS,
                                     'retval': FUNC_RETVAL},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)
        self.assertEqual(response.data['function'], FUNC_NAME)

        # verify the function now appears in the function list
        response = self.client.get('/odaweb/api/functions/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')

        funcs = {func['vma']: func for func in response.data}

        self.assertEqual(funcs[FUNC_ADDR]['name'], FUNC_NAME)
        self.assertEqual(funcs[FUNC_ADDR]['vma'], FUNC_ADDR)
        self.assertEqual(funcs[FUNC_ADDR]['args'], FUNC_ARGS)
        self.assertEqual(funcs[FUNC_ADDR]['retval'], FUNC_RETVAL)

        # verify the function now appears in the symbol list
        response = self.client.get('/odaweb/api/symbols/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        syms = {sym['vma']: sym for sym in response.data}

        self.assertEqual(syms[FUNC_ADDR]['name'], FUNC_NAME)
        self.assertEqual(syms[FUNC_ADDR]['vma'], FUNC_ADDR)
        self.assertEqual(syms[FUNC_ADDR]['type'].lower(), 't')

    def test_edit_function(self):
        # the 'usage' function pre-exists at this address
        # FUNC_ADDR = 0x401ba0
        FUNC_ADDR = 4201376
        FUNC_NAME = 'something_completely_different'
        FUNC_ARGS = 'uint8_t,uint16_t'
        FUNC_RETVAL = 'uint32_t'

        # edit an existing function
        response = self.client.patch('/odaweb/api/functions/1/',
                                     {'revision': 0,
                                      'short_name': 'mkdir',
                                      'vma': FUNC_ADDR,
                                      'name': FUNC_NAME,
                                      'args': FUNC_ARGS,
                                      'retval': FUNC_RETVAL},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], None)

        # verify the function updates appear in the function list
        response = self.client.get('/odaweb/api/functions/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')

        funcs = {func['vma']: func for func in response.data}

        self.assertEqual(funcs[FUNC_ADDR]['name'], FUNC_NAME)
        self.assertEqual(funcs[FUNC_ADDR]['vma'], FUNC_ADDR)
        self.assertEqual(funcs[FUNC_ADDR]['args'], FUNC_ARGS)
        self.assertEqual(funcs[FUNC_ADDR]['retval'], FUNC_RETVAL)

        # verify the function also appears correctly in the symbol list
        response = self.client.get('/odaweb/api/symbols/',
                                   {'revision': 0, 'short_name': 'mkdir'},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        syms = {sym['vma']: sym for sym in response.data}

        self.assertEqual(syms[FUNC_ADDR]['name'], FUNC_NAME)
        self.assertEqual(syms[FUNC_ADDR]['vma'], FUNC_ADDR)
        self.assertEqual(syms[FUNC_ADDR]['type'].lower(), 't')

    def test_make_function_on_data(self):
        # TODO
        pass

    def test_make_function_that_already_exists(self):
        # TODO
        pass

    def test_make_function_at_illegal_address(self):
        # TODO
        pass

    def test_make_function_verify_args(self):
        # TODO
        pass

    def test_make_function_verify_retval(self):
        # TODO
        pass
