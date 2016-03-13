import sys
import unittest

import vdf
from collections import OrderedDict

u = str if sys.version_info >= (3,) else unicode


class BinaryVDF(unittest.TestCase):
    def test_BASE_INT(self):
        repr(vdf.BASE_INT())

    def test_simple(self):
        pairs = [
            ('a', 'test'),
            ('a2', b'\xff\xfe0\x041\x042\x043\x04'.decode('utf-16')),
            ('bb', 1),
            ('bb2', -500),
            ('ccc', 1.0),
            ('dddd', vdf.POINTER(1234)),
            ('fffff', vdf.COLOR(1234)),
            ('gggggg', vdf.UINT_64(1234)),
        ]

        data = OrderedDict(pairs)
        data['level1-1'] = OrderedDict(pairs)
        data['level1-1']['level2-1'] = OrderedDict(pairs)
        data['level1-1']['level2-2'] = OrderedDict(pairs)
        data['level1-2'] = OrderedDict(pairs)

        result = vdf.binary_loads(vdf.binary_dumps(data), mapper=OrderedDict)

        self.assertEqual(data, result)

    def test_loads_empty(self):
        self.assertEqual(vdf.binary_loads(b''), {})

    def test_dumps_empty(self):
        self.assertEqual(vdf.binary_dumps({}), b'')

    def test_dumps_unicode(self):
        self.assertEqual(vdf.binary_dumps({u('a'): u('b')}), b'\x01a\x00b\x00\x08')

    def test_dumps_key_invalid_type(self):
        with self.assertRaises(TypeError):
            vdf.binary_dumps({1:1})
        with self.assertRaises(TypeError):
            vdf.binary_dumps({None:1})

    def test_dumps_value_invalid_type(self):
        with self.assertRaises(TypeError):
            vdf.binary_dumps({'': None})

    def test_loads_unbalanced_nesting(self):
        with self.assertRaises(SyntaxError):
            vdf.binary_loads(b'\x00a\x00\x00b\x00\x08')
        with self.assertRaises(SyntaxError):
            vdf.binary_loads(b'\x00a\x00\x00b\x00\x08\x08\x08\x08')

    def test_loads_unknown_type(self):
        with self.assertRaises(SyntaxError):
            vdf.binary_loads(b'\x33a\x00\x08')

    def test_loads_unterminated_string(self):
        with self.assertRaises(SyntaxError):
            vdf.binary_loads(b'\x01abbbb')

    def test_loads_type_checks(self):
        with self.assertRaises(TypeError):
            vdf.binary_loads(None)
        with self.assertRaises(TypeError):
            vdf.binary_loads(b'', mapper=list)
