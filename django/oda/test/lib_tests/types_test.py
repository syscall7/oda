from oda.libs.odb.structures.types import *
from oda.test.oda_test_case import OdaLibTestCase

class TestTypes(OdaLibTestCase):

    def test_builtin_types(self):
        bytes = b'\x01\x23\x45\x67\x89\xab\xcd\xef'

        # TODO: Test little endian in addition to big endian

        # unsigned
        self.assertEqual('0x01', uint8_t().format(bytes))
        self.assertEqual('0x0123', uint16_t().format(bytes))
        self.assertEqual('0x01234567', uint32_t().format(bytes))
        self.assertEqual('0x0123456789abcdef', uint64_t().format(bytes))

        # signed
        self.assertEqual('1', int8_t().format(bytes))
        self.assertEqual('291', int16_t().format(bytes))
        self.assertEqual('19088743', int32_t().format(bytes))
        self.assertEqual('81985529216486895', int64_t().format(bytes))
