#!/usr/bin/env python
from __future__ import print_function

# a simple parser for Valve's KeyValue format
# https://developer.valvesoftware.com/wiki/KeyValues
#
# author: Rossen Popov, 2014
#
# use at your own risk

__version__ = "1.0"

import re
import sys

if sys.version_info.major >= 3:
    from io import IOBase
else:
    IOBase = file

from codecs import BOM, BOM_BE, BOM_LE, BOM_UTF8, BOM_UTF16, BOM_UTF16_BE
from codecs import BOM_UTF16_LE, BOM_UTF32, BOM_UTF32_BE, BOM_UTF32_LE


BOMS = [
    BOM,
    BOM_BE,
    BOM_LE,
    BOM_UTF8,
    BOM_UTF16,
    BOM_UTF16_BE,
    BOM_UTF16_LE,
    BOM_UTF32,
    BOM_UTF32_BE,
    BOM_UTF32_LE,
]

###############################################
#
# Takes a file or str and returns dict
#
# Function assumes valid VDF as input.
# Invalid VDF will result in unexpected output
#
###############################################


def parse(source):
    if isinstance(source, IOBase):
        lines = source.readlines()
    elif isinstance(source, str):
        lines = source.split('\n')
    else:
        raise ValueError("Expected parametar to be file or str")

    # check first line BOM and remove
    for bom in BOMS:
        if lines[0][:len(bom)] == bom:
            lines[0] = lines[0][len(bom):]
            break

    # init
    obj = dict()
    stack = [obj]
    expect_bracket = False

    re_keyvalue = re.compile(r'^"((?:\\.|[^\\"])*)"[ \t]*"((?:\\.|[^\\"])*)(")?')
    re_key = re.compile(r'^"((?:\\.|[^\\"])*)"')

    itr = iter(lines)

    for line in itr:
        line = line.strip()

        # skip empty and comment lines
        if line == "" or line[0] == '/':
            continue

        # one level deeper
        if line[0] == "{":
            expect_bracket = False
            continue

        if expect_bracket:
            raise SyntaxError("vdf.parse: invalid syntax")

        # one level back
        if line[0] == "}":
            stack.pop()
            continue

        # parse keyvalue pairs
        if line[0] == '"':
            while True:
                m = re_keyvalue.match(line)

                # we've matched a simple keyvalue pair, map it to the last dict obj in the stack
                if m:
                    # if the value is line consume one more line and try to match again,
                    # until we get the KeyValue pair
                    if m.group(3) is None:
                        if sys.version_info.major >= 3:
                            line += "\n" + itr.__next__()
                        else:
                            line += "\n" + itr.next()
                        continue

                    stack[-1][m.group(1)] = m.group(2)

                # we have a key with value in parenthesis, so we make a new dict obj (level deeper)
                else:
                    m = re_key.match(line)

                    if not m:
                        raise SyntaxError("vdf.parse: invalid syntax")

                    key = m.group(1)

                    stack[-1][key] = dict()
                    stack.append(stack[-1][key])
                    expect_bracket = True

                # exit the loop
                break

    if len(stack) != 1:
        raise SyntaxError("vdf.parse: unclosed parenthasis or quotes")

    return obj


def loads(fp):
    assert isinstance(fp, str)
    return parse(fp)


def load(fp):
    assert isinstance(fp, IOBase)
    return parse(fp)

###############################################
#
# Take a dict, reuturns VDF in str buffer
#
# dump(dict(), pretty=True) for indented VDF
#
###############################################


def dumps(a, **kwargs):
    pretty = kwargs.get("pretty", False)

    if not isinstance(pretty, bool):
        raise ValueError("Pretty parameter expects boolean value")

    return _dump(a, pretty)


def _dump(a, pretty=False, level=0):
    if not isinstance(a, dict):
        raise ValueError("Expected data to be a dict")

    indent = "\t"
    buf = ""
    line_indent = ""

    if pretty:
        line_indent = indent * level

    for key in a:
        if isinstance(a[key], dict):
            buf += '%s"%s"\n%s{\n%s%s}\n' % (line_indent, key, line_indent, _dump(a[key], pretty, level+1), line_indent)
        else:
            buf += '%s"%s" "%s"\n' % (line_indent, key, str(a[key]))

    return buf


def dump(data, f, **kwargs):
    with f:
        f.write(dumps(data, **kwargs))

###############################################
#
# Testing initiative
#
###############################################


def test():
    tests = [
                # empty test
                [ '' , {} ],
                [ {} ,  '' ],

                # simple key and values
                [ {1:1}, '"1" "1"\n'],
                [ {"a":"1","b":"2"} , '"a" "1"\n"b" "2"\n' ],

                # nesting
                [ {"a":{"b":{"c":{"d":"1","e":"2"}}}} , '"a"\n{\n"b"\n{\n"c"\n{\n"e" "2"\n"d" "1"\n}\n}\n}\n' ],
                [ '"a"\n{\n"b"\n{\n"c"\n{\n"e" "2"\n"d" "1"\n}\n}\n}\n"b" "2"' , {"a":{"b":{"c":{"d":"1","e":"2"}}},"b":"2"} ],

                # ignoring comment lines
                [ "//comment text\n//comment", {} ],
                [ '"a" "b" //comment text', {"a":"b"} ],
                [ '//comment\n"a" "1"\n"b" "2" //comment' , {"a":"1","b":"2"} ],
                [ '"a"\n{//comment\n}//comment' , {"a":{}} ],
                [ '"a" //comment\n{\n}' , {"a":{}} ],


                # new linesi n value
                [ r'"a" "xx\"xxx"', {"a":r'xx\"xxx'} ],
                [ '"a" "xx\\"\nxxx"', {"a":'xx\\"\nxxx'} ],
                [ '"a" "\n\n\n\n"', {"a":'\n\n\n\n'} ]
            ]

    for test, expected in tests:
        out = None

        try:
            if isinstance(test, dict):
                out = dumps(test)
            else:
                out = loads(test)
        except:
            print("Test falure (exception):\n\n%s" % str(test))
            raise

        if expected != out:
            print("Test falure (ouput mismatch):\n\n%s" % str(test))
            print("\nOutput:\n\n%s" % str(out))
            print("\nExpected:\n\n%s\n" % str(expected))

            raise Exception("Output differs from expected result")

    return True
