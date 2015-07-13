"""
Module for deserializing/serializing to and from VDF
"""
__version__ = "1.9"
__author__ = "Rossen Georgiev"

import re
import sys
from io import StringIO as unicodeIO

# Py2 & Py3 compability
if sys.version_info[0] >= 3:
    string_type = str
    BOMS = '\ufffe\ufeff'

    def bomlen(line):
        return len(line) - len(line.lstrip(BOMS))
else:
    from cStringIO import StringIO as strIO
    string_type = basestring
    BOMS = '\xef\xbb\xbf\xff\xfe\xfe\xff'
    BOMS_UNICODE = '\\ufffe\\ufeff'.decode('unicode-escape')

    def bomlen(line):
        return len(line) - len(line.lstrip(BOMS if isinstance(line, str) else BOMS_UNICODE))


def parse(source, mapper=dict):
    """
    Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a VDF)
    to a Python object.

    ``mapper`` specifies the Python object used after deserializetion. ``dict` is
    used by default. Alternatively, ``collections.OrderedDict`` can be used if you
    wish to preserve key order. Or any object that acts like a ``dict``.
    """
    if not issubclass(mapper, dict):
        raise TypeError("Expected mapper to be subclass of dict, got %s", type(mapper))
    if hasattr(source, 'read'):
        fp = source
    elif isinstance(source, string_type):
        try:
            fp = unicodeIO(source)
        except TypeError:
            fp = strIO(source)
    else:
        raise TypeError("Expected source to be str or file-like object")

    # skip past BOMs
    fp.seek(bomlen(fp.read(10)))

    # init
    stack = [mapper()]
    expect_bracket = False

    re_keyvalue = re.compile(r'^("(?P<qkey>(?:\\.|[^\\"])+)"|(?P<key>[a-z0-9\-\_]+))'
                             r'([ \t]*('
                             r'"(?P<qval>(?:\\.|[^\\"])*)(?P<vq_end>")?'
                             r'|(?P<val>[a-z0-9\-\_]+)'
                             r'))?'
                             )

    for line in fp:
        line = line.lstrip()

        # skip empty and comment lines
        if line == "" or line[0:2] == '//':
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
        while True:
            match = re_keyvalue.match(line)

            if not match:
                raise SyntaxError("vdf.parse: invalid syntax")

            key = match.group('key') if match.group('qkey') is None else match.group('qkey')
            val = match.group('val') if match.group('qval') is None else match.group('qval')

            # we have a key with value in parenthesis, so we make a new dict obj (level deeper)
            if val is None:
                stack[-1][key] = mapper()
                stack.append(stack[-1][key])
                expect_bracket = True

            # we've matched a simple keyvalue pair, map it to the last dict obj in the stack
            else:
                # if the value is line consume one more line and try to match again,
                # until we get the KeyValue pair
                if match.group('vq_end') is None and match.group('qval') is not None:
                    line += next(fp)
                    continue

                stack[-1][key] = val

            # exit the loop
            break

    if len(stack) != 1:
        raise SyntaxError("vdf.parse: unclosed parenthasis or quotes")

    return stack.pop()


def loads(fp, **kwargs):
    """
    Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a VDF) to a Python object.
    """
    assert isinstance(fp, string_type), "Expected a str"
    return parse(fp, **kwargs)


def load(fp, **kwargs):
    """
    Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a VDF)
    to a Python object.
    """
    assert hasattr(fp, 'read'), "Expected fp to have readlines() method"
    return parse(fp, **kwargs)


def dumps(data, pretty=False):
    """
    Serialize ``obj`` to VDF formatted ``str``.
    """
    if not isinstance(data, dict):
        raise TypeError("Expected data to be an instance of``dict``")
    if not isinstance(pretty, bool):
        raise TypeError("Expected pretty to be bool")

    return ''.join(_dump_gen(data, pretty))


def dump(data, fp, pretty=False):
    """
    Serialize ``obj`` as a VDF formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).
    """
    if not isinstance(data, dict):
        raise TypeError("Expected data to be an instance of``dict``")
    if not hasattr(fp, 'write'):
        raise TypeError("Expected fp to have write() method")

    for chunk in _dump_gen(data, pretty):
        fp.write(chunk)


def _dump_gen(data, pretty=False, level=0):
    indent = "\t"
    line_indent = ""

    if pretty:
        line_indent = indent * level

    for key, value in data.items():
        if isinstance(value, dict):
            yield '%s"%s"\n%s{\n' % (line_indent, key, line_indent)
            for chunk in _dump_gen(value, pretty, level+1):
                yield chunk
            yield "%s}\n" % line_indent
        else:
            yield '%s"%s" "%s"\n' % (line_indent, key, value)
