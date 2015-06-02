#!/usr/bin/env python
from __future__ import print_function

# a simple parser for Valve's KeyValue format
# https://developer.valvesoftware.com/wiki/KeyValues
#
# author: Rossen Popov, 2014
#
# use at your own risk

__version__ = "1.6"

import re
import sys

# Py2 & Py3 compability
if sys.version_info[0] >= 3:
    string_type = str
    next_method_name = '__next__'
    BOMS = '\ufffe\ufeff'

    def strip_bom(line):
        return line.lstrip(BOMS)
else:
    string_type = basestring
    next_method_name = 'next'
    BOMS = '\xef\xbb\xbf\xff\xfe\xfe\xff'
    BOMS_UNICODE = '\\ufffe\\ufeff'.decode('unicode-escape')

    def strip_bom(line):
        return line.lstrip(BOMS if isinstance(line, str) else BOMS_UNICODE)

###############################################
#
# Takes a file or str and returns dict
#
# Function assumes valid VDF as input.
# Invalid VDF will result in unexpected output
#
###############################################


def parse(source, mapper=dict):
    if not issubclass(mapper, dict):
        raise TypeError("Expected mapper to be subclass of dict, got %s", type(mapper))
    if hasattr(source, 'readlines'):
        lines = source.readlines()
    elif isinstance(source, string_type):
        lines = source.split('\n')
    else:
        raise TypeError("Expected source to be str or have readlines() method")

    # strip annoying BOMS
    lines[0] = strip_bom(lines[0])

    # init
    obj = mapper()
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
            if len(stack) > 1:
                stack.pop()
                continue

            raise SyntaxError("vdf.parse: one too many closing parenthasis")

        # parse keyvalue pairs
        if line[0] == '"':
            while True:
                m = re_keyvalue.match(line)

                # we've matched a simple keyvalue pair, map it to the last dict obj in the stack
                if m:
                    # if the value is line consume one more line and try to match again,
                    # until we get the KeyValue pair
                    if m.group(3) is None:
                        line += "\n" + getattr(itr, next_method_name)()
                        continue

                    stack[-1][m.group(1)] = m.group(2)

                # we have a key with value in parenthesis, so we make a new dict obj (level deeper)
                else:
                    m = re_key.match(line)

                    if not m:
                        raise SyntaxError("vdf.parse: invalid syntax")

                    key = m.group(1)

                    stack[-1][key] = mapper()
                    stack.append(stack[-1][key])
                    expect_bracket = True

                # exit the loop
                break

    if len(stack) != 1:
        raise SyntaxError("vdf.parse: unclosed parenthasis or quotes")

    return obj


def loads(fp, **kwargs):
    assert isinstance(fp, string_type), "Expected a str"
    return parse(fp, **kwargs)


def load(fp, **kwargs):
    assert hasattr(fp, 'readlines'), "Expected fp to have readlines() method"
    return parse(fp, **kwargs)

###############################################
#
# Take a dict, reuturns VDF in str buffer
#
# dump(dict(), pretty=True) for indented VDF
#
###############################################


def dumps(data, pretty=False, level=0):
    if not isinstance(data, dict):
        raise TypeError("Expected data to be a dict or subclass of dict")
    if not isinstance(pretty, bool):
        raise TypeError("Expected pretty to be bool")

    indent = "\t"
    buf = ""
    line_indent = ""

    if pretty:
        line_indent = indent * level

    for key, value in data.items():
        if isinstance(value, dict):
            buf += '%s"%s"\n%s{\n%s%s}\n' % (
                line_indent, key, line_indent, dumps(value, pretty, level+1), line_indent
            )
        else:
            buf += '%s"%s" "%s"\n' % (line_indent, key, value)

    return buf


def dump(data, fp, pretty=False):
    if not isinstance(data, dict):
        raise TypeError("Expected data to be a dict")
    if not hasattr(fp, 'write'):
        raise TypeError("Expected fp to have write() method")

    fp.write(dumps(data, pretty))
