#!/usr/bin/env python

import argparse
import sys
import json
import vdf


def main():
    p = argparse.ArgumentParser(prog='vdf2json')

    p.add_argument('infile', nargs='?', type=argparse.FileType('rb'), default=sys.stdin, help="VDF")
    p.add_argument('outfile', nargs='?', type=argparse.FileType('wb'), default=sys.stdout, help="JSON (utf8)")

    p.add_argument('-p', '--pretty', help='pretty json output', action='store_true')
    p.add_argument('-ei', default='utf-8', type=str, metavar='encoding', help='E.g.: utf8, utf-16le, etc')

    args = p.parse_args()

    data = vdf.loads(args.infile.read().decode(args.ei))

    json.dump(data, args.outfile, indent=4 if args.pretty else 0, ensure_ascii=False)


if __name__ == '__main__':
    main()
