#!/usr/bin/env python
from __future__ import print_function

# a simple parser for Valve's KeyValue format
# https://developer.valvesoftware.com/wiki/KeyValues
#
# author: Rossen Popov, 2014
#
# use at your own risk

__version__ = "1.3"

import re
import sys

# Py2 & Py3 compability
if sys.version_info[0] >= 3:
    from io import IOBase as file_type
    string_type = str
    next_method_name = '__next__'
    BOMS = ('\ufffe', '\ufeff')

    def strip_bom(line):
        if line.startswith(BOMS):
            return line[1:]
        return line

else:
    from StringIO import StringIO
    file_type = (file, StringIO)
    string_type = basestring
    next_method_name = 'next'
    BOMS = ('\xff\xfe', '\xfe\xff')
    BOMS_UNICODE = ['\\ufffe', '\\ufeff']
    BOMS_UNICODE = tuple(map(lambda x: x.decode('unicode-escape'), BOMS_UNICODE))

    def strip_bom(line):
        if isinstance(line, str):
            if line.startswith(BOMS):
                return line[2:]
        else:
            if line.startswith(BOMS_UNICODE):
                    return line[1:]
        return line

###############################################
#
# Takes a file or str and returns dict
#
# Function assumes valid VDF as input.
# Invalid VDF will result in unexpected output
#
###############################################


def parse(source):
    if isinstance(source, file_type):
        lines = source.readlines()
    elif isinstance(source, string_type):
        lines = source.split('\n')
    else:
        raise ValueError("Expected parametar to be file or str")

    # strip anoying BOMS
    lines[0] = strip_bom(lines[0])

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

                    stack[-1][key] = dict()
                    stack.append(stack[-1][key])
                    expect_bracket = True

                # exit the loop
                break

    if len(stack) != 1:
        raise SyntaxError("vdf.parse: unclosed parenthasis or quotes")

    return obj


def loads(fp):
    assert isinstance(fp, string_type)
    return parse(fp)


def load(fp):
    assert isinstance(fp, file_type)
    return parse(fp)

###############################################
#
# Take a dict, reuturns VDF in str buffer
#
# dump(dict(), pretty=True) for indented VDF
#
###############################################


def dumps(data, pretty=False, level=0):
    if not isinstance(data, dict):
        raise ValueError("Expected data to be a dict")
    if not isinstance(pretty, bool):
        raise ValueError("Pretty parameter expects boolean value")

    indent = "\t"
    buf = ""
    line_indent = ""

    if pretty:
        line_indent = indent * level

    for key in data:
        if isinstance(data[key], dict):
            buf += '%s"%s"\n%s{\n%s%s}\n' % (
                line_indent, key, line_indent, dumps(data[key], pretty, level+1), line_indent
            )
        else:
            buf += '%s"%s" "%s"\n' % (line_indent, key, data[key])

    return buf


def dump(data, fp, pretty=True):
    if not isinstance(data, dict):
        raise ValueError("Expected data to be a dict")
    if not isinstance(fp, file_type):
        raise ValueError("Expected fp to be file")

    fp.write(dumps(data, pretty))
