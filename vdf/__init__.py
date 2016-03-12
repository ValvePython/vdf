"""
Module for deserializing/serializing to and from VDF
"""
__version__ = "1.10"
import struct
__author__ = "Rossen Georgiev"

import re
import sys
from io import StringIO as unicodeIO

# Py2 & Py3 compability
if sys.version_info[0] >= 3:
    string_type = str
    BOMS = '\ufffe\ufeff'

    def strip_bom(line):
        return line.lstrip(BOMS)
else:
    from StringIO import StringIO as strIO
    string_type = basestring
    BOMS = '\xef\xbb\xbf\xff\xfe\xfe\xff'
    BOMS_UNICODE = '\\ufffe\\ufeff'.decode('unicode-escape')

    def strip_bom(line):
        return line.lstrip(BOMS if isinstance(line, str) else BOMS_UNICODE)


def parse(fp, mapper=dict):
    """
    Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a VDF)
    to a Python object.

    ``mapper`` specifies the Python object used after deserializetion. ``dict` is
    used by default. Alternatively, ``collections.OrderedDict`` can be used if you
    wish to preserve key order. Or any object that acts like a ``dict``.
    """
    if not issubclass(mapper, dict):
        raise TypeError("Expected mapper to be subclass of dict, got %s", type(mapper))
    if not hasattr(fp, 'readline'):
        raise TypeError("Expected fp to be a file-like object supporting line iteration")

    stack = [mapper()]
    expect_bracket = False

    re_keyvalue = re.compile(r'^("(?P<qkey>(?:\\.|[^\\"])+)"|(?P<key>[a-z0-9\-\_]+))'
                             r'([ \t]*('
                             r'"(?P<qval>(?:\\.|[^\\"])*)(?P<vq_end>")?'
                             r'|(?P<val>[a-z0-9\-\_]+)'
                             r'))?',
                             flags=re.I)

    for idx, line in enumerate(fp):
        if idx == 0:
            line = strip_bom(line)

        line = line.lstrip()

        # skip empty and comment lines
        if line == "" or line[0] == '/':
            continue

        # one level deeper
        if line[0] == "{":
            expect_bracket = False
            continue

        if expect_bracket:
            raise SyntaxError("vdf.parse: expected openning bracket (line %d)" % (idx + 1))

        # one level back
        if line[0] == "}":
            if len(stack) > 1:
                stack.pop()
                continue

            raise SyntaxError("vdf.parse: one too many closing parenthasis (line %d)" % (idx + 1))

        # parse keyvalue pairs
        while True:
            match = re_keyvalue.match(line)

            if not match:
                raise SyntaxError("vdf.parse: invalid syntax (line %d)" % (idx + 1))

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
        raise SyntaxError("vdf.parse: unclosed parenthasis or quotes (EOF)")

    return stack.pop()


def _read_till_seperator(fp, seperator="\x00", buffersize=2048):
    tmp = ""
    start_offset = fp.tell() 
    _sep_length = len(seperator)
    while True:
        data = fp.read(buffersize)
        if not data:
            return tmp
        tmp += data
        index = tmp.find(seperator)
        if index != -1:
            fp.seek(start_offset + index + _sep_length)
            return tmp[:index]


BIN_NONE = '\x00'
BIN_STRING = '\x01'
BIN_INT32 = '\x02'
BIN_FLOAT32 = '\x03'
BIN_POINTER = '\x04'
BIN_WIDESTRING = '\x05'
BIN_COLOR = '\x06'
BIN_UINT64 = '\x07'
BIN_END = '\x08'
def parse_binary(source, mapper=dict):
    """
    Deserialize ``source`` (a ``str`` or file like object containing a VDF in "binary form")
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
        fp = strIO(source)
    else:
        raise TypeError("Expected source to be str or file-like object")

    # init
    stack = [mapper()]    
    _read_int32 = struct.Struct('<i').unpack
    _read_uint64 = struct.Struct('<Q').unpack
    _read_float32 = struct.Struct('<f').unpack

    while True:
        obj_type = fp.read(1)
        if obj_type == BIN_END:
            if len(stack) > 1:
                stack.pop()
            else:
                return stack[0]
            continue
        
        obj_name = _read_till_seperator(fp, seperator="\x00")
        if obj_type == BIN_NONE:
            stack[-1][obj_name] = mapper()
            stack.append(stack[-1][obj_name])
        elif obj_type == BIN_STRING:
            value = _read_till_seperator(fp, seperator="\x00")
            stack[-1][obj_name] = value
        elif obj_type == BIN_INT32:
            stack[-1][obj_name] = _read_int32(fp.read(4))[0]
        elif obj_type == BIN_UINT64:
            stack[-1][obj_name] = _read_uint64(fp.read(8))[0]
        elif obj_type == BIN_FLOAT32:
            stack[-1][obj_name] = _read_float32(fp.read(4))[0]
        elif obj_type in (BIN_POINTER, BIN_WIDESTRING, BIN_COLOR):
            # TODO: Check what they are and implement
            raise SyntaxError('vdf.parse_binary: type not supported #%i' % ord(obj_type))
        else:
            raise SyntaxError('vdf.parse_binary: invalid type code #%i' % ord(obj_type))
       
    return stack.pop()


def loads(s, **kwargs):
    """
    Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a JSON
    document) to a Python object.
    """
    if not isinstance(s, string_type):
        raise TypeError("Expected s to be a str, got %s", type(s))

    try:
        fp = unicodeIO(s)
    except TypeError:
        fp = strIO(s)

    return parse(fp, **kwargs)


def load(fp, **kwargs):
    """
    Deserialize ``fp`` (a ``.readline()``-supporting file-like object containing
    a JSON document) to a Python object.
    """
    return parse(fp, **kwargs)


def dumps(obj, pretty=False):
    """
    Serialize ``obj`` as a VDF formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).
    """
    if not isinstance(obj, dict):
        raise TypeError("Expected data to be an instance of``dict``")
    if not isinstance(pretty, bool):
        raise TypeError("Expected pretty to be bool")

    return ''.join(_dump_gen(obj, pretty))


def dump(obj, fp, pretty=False):
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    """
    if not isinstance(obj, dict):
        raise TypeError("Expected data to be an instance of``dict``")
    if not hasattr(fp, 'write'):
        raise TypeError("Expected fp to have write() method")

    for chunk in _dump_gen(obj, pretty):
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
            
            
def _dump_gen_binary(data, level=0):
    """
    Serializes an dict (or an extension thereof) as binary vdf.
    Every scalar need to be a tuple or list with the length 2 in the form:
        (``data_type``, ``value``)
        where ``data_type`` is one of (BIN_INT32, BIN_UINT64, BIN_FLOAT32, BIN_STRING)
    """
    type_mapper = {
                   BIN_INT32: struct.Struct('<i').pack,
                   BIN_UINT64: struct.Struct('<Q').pack,
                   BIN_FLOAT32: struct.Struct('<f').pack,
                   BIN_STRING: lambda x: x + "\x00",
                   }
    for key, value in data.items():
        if isinstance(value, dict):
            yield "".join((BIN_NONE, key, "\x00"))
            for chunk in _dump_gen_binary(value, level+1):
                yield chunk
            yield BIN_END
        else:
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise TypeError("Values need to be a list or tuple with the length 2.")
            type_code, type_data = value
            if type_code in type_mapper:
                yield "".join((type_code, key, "\x00", type_mapper[type_code](type_data)))
            else:
                raise TypeError('Unsupported type')
