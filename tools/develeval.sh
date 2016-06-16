#!/bin/bash

# Convert CoNLL-formatted data into BC2GM format and evaluate using
# BC2GM evaluation script alt_eval.perl on development data.

set -e
set -u

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BC2GMDIR="$SCRIPTDIR/.."
DATADIR="$BC2GMDIR/devel-split/devel/"

CONLLFILE=$1

BC2GMFILE=$(mktemp)
trap "rm -rf $BC2GMFILE" EXIT

python "$SCRIPTDIR"/conll_to_bc2gm.py $CONLLFILE "$DATADIR"/devel.in \
    > $BC2GMFILE

$BC2GMDIR/original-data/train/alt_eval.perl \
    -gene "$DATADIR"/GENE.eval \
    -altgene "$DATADIR"/ALTGENE.eval \
    $BC2GMFILE
