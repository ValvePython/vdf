import unittest
import mock
import sys

try:
        from StringIO import StringIO
except ImportError:
        from io import StringIO

import vdf


class testcase_helpers_load(unittest.TestCase):
    def setUp(self):
        self.f = StringIO()

    def tearDown(self):
        self.f.close()

    @mock.patch("vdf.parse")
    def test_routine_loads(self, mock_parse):
        vdf.loads("")
        mock_parse.assert_called_with("")

    def test_routine_loads_assert(self):
        for t in [5, 5.5, 1.0j, None, [], (), {}, lambda: 0, sys.stdin, self.f]:
            self.assertRaises(AssertionError, vdf.loads, t)

    @mock.patch("vdf.parse")
    def test_routine_load(self, mock_parse):
        vdf.load(sys.stdin)
        mock_parse.assert_called_with(sys.stdin)

        vdf.load(self.f)
        mock_parse.assert_called_with(self.f)

    def test_routine_load_assert(self):
        for t in [5, 5.5, 1.0j, None, [], (), {}, lambda: 0, '']:
            self.assertRaises(AssertionError, vdf.load, t)


class testcase_helpers_dump(unittest.TestCase):
    def setUp(self):
        self.f = StringIO()

    def tearDown(self):
        self.f.close()

    def test_routine_dumps_asserts(self):
        for x in [5, 5.5, 1.0j, True, None, (), {}, lambda: 0, sys.stdin, self.f]:
            for y in [5, 5.5, 1.0j, None, [], (), {}, lambda: 0, sys.stdin, self.f]:
                self.assertRaises(ValueError, vdf.dumps, x, y)

    def test_routine_dump_asserts(self):
        for x in [5, 5.5, 1.0j, True, None, (), {}, lambda: 0, sys.stdin, self.f]:
            for y in [5, 5.5, 1.0j, True, None, [], (), {}, lambda: 0]:
                self.assertRaises(ValueError, vdf.dump, x, y)

    def test_routine_dump_writing(self):
        src = {"asd": "123"}
        expected = vdf.dumps(src)

        vdf.dump(src, self.f)
        self.f.seek(0)

        self.assertEqual(expected, self.f.read())


class testcase_parse_routine(unittest.TestCase):
    def test_parse_bom_removal(self):
        for mark in vdf.BOMS:
            result = vdf.loads(mark + '"asd" "123"')
            self.assertEqual(result, {'asd': '123'})

        if sys.version_info[0] is 2:
            for mark in vdf.BOMS_UNICODE:
                result = vdf.loads(mark + '"asd" "123"')
                self.assertEqual(result, {'asd': '123'})

    def test_parse_asserts(self):
        for t in [5, 5.5, 1.0j, True, None, (), {}, lambda: 0]:
            self.assertRaises(ValueError, vdf.parse, t)

    def test_parse_file_source(self):
        self.assertEqual(vdf.parse(StringIO(" ")), {})


class testcase_VDF(unittest.TestCase):
    def test_format(self):
        tests = [
            # empty test
            ['', {}],

            # simple key and values
            [
                {'1': '1'},
                '"1" "1"\n'
            ],
            [
                {"a": "1", "b": "2"},
                '"a" "1"\n"b" "2"\n'
            ],

            # nesting
            [
                {"a": {"b": {"c": {"d": "1", "e": "2"}}}},
                '"a"\n{\n"b"\n{\n"c"\n{\n"e" "2"\n"d" "1"\n}\n}\n}\n'
            ],
            [
                '"a"\n{\n"b"\n{\n"c"\n{\n"e" "2"\n"d" "1"\n}\n}\n}\n"b" "2"\n',
                {"a": {"b": {"c": {"d": "1", "e": "2"}}}, "b": "2"}
            ],

            # ignoring comment lines
            [
                "//comment text\n//comment",
                {}
            ],
            [
                "//comment text\n//comment",
                {}
            ],
            [
                '"a" "b" //comment text',
                {"a": "b"}],
            [
                '//comment\n"a" "1"\n"b" "2" //comment',
                {"a": "1", "b": "2"}
            ],
            [
                '"a"\n{//comment\n}//comment',
                {"a": {}}
            ],
            [
                '"a" //comment\n{\n}',
                {"a": {}}
            ],


            # new lines in value
            [
                r'"a" "xx\"xxx"',
                {"a": r'xx\"xxx'}
            ],
            [
                '"a" "xx\\"\nxxx"',
                {"a": 'xx\\"\nxxx'}
            ],
            [
                '"a" "\n\n\n\n"',
                {"a": '\n\n\n\n'}
            ],
        ]

        for test, expected in tests:
            if isinstance(test, dict):
                self.assertEqual(vdf.dumps(test), expected)
            else:
                self.assertEqual(vdf.loads(test), expected)

    def test_parse_exceptions(self):
        tests = [

            # expect bracket - invalid syntax
            '"asd"\n"zxc" "333"\n"',

            # invalid syntax
            '"asd" "123"\n"zxc" "333"\n"',

            # unclosed parenthasis
            '"asd"\n{\n"zxc" "333"\n'
        ]

        for test in tests:
            self.assertRaises(SyntaxError, vdf.parse, test)
