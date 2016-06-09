#!/usr/bin/env python

from __future__ import print_function

import sys
import io

from os import path

from bc2gm import load_bc2gm

def main(argv):
    if len(argv) != 4:
        print('Usage: bc2gm2ann TXTFILE ANNFILE OUTDIR', file=sys.stderr)
        return 1
    txtfn, annfn, outdir = argv[1:]

    if not path.isdir(outdir):
        print('%s is not a directory' % outdir, file=sys.stderr)
        return 1

    sentences = load_bc2gm(txtfn, annfn)

    for s in sentences:
        txtout = path.join(outdir, s.id+'.txt')
        with io.open(txtout, 'wt', encoding='utf-8') as out:
            out.write(s.text+'\n')
        annout = path.join(outdir, s.id+'.ann')
        with io.open(annout, 'wt', encoding='utf-8') as out:
            for a in s.to_standoff():
                out.write(a+'\n')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
