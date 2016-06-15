# bc2gm-corpus

Work related to the BioCreative II Gene Mention corpus

## Source data

The original BC2GM corpus data packages `bc2GMtrain_1.1.tar.gz` and
`bc2GMtest_1.0.tar.gz` were downloaded from
<http://www.biocreative.org/resources/corpora/biocreative-ii-corpus/>
and unpacked into `original-data`.

## Standoff data

The original data was initially converted into the BioNLP shared
task-flavored standoff format with

    mkdir -p standoff/{train,devel,test}
    python tools/bc2gm2ann.py original-data/train/{train.in,GENE.eval} standoff/train/
    python tools/bc2gm2ann.py original-data/test/{test.in,GENE.eval} standoff/test/

and a set of 2500 documents was then moved from `standoff/train` to
`standoff/devel` as a development set.

## Combined data

A version of the data combining the GENE and ALTGENE versions of the data
was created as

    mkdir -p combined-data/{train,test}
    cat original-data/train/{GENE,ALTGENE}.eval | sort > combined-data/train/GENE.eval
    cp original-data/train/train.in combined-data/train/
    cat original-data/test/{GENE,ALTGENE}.eval | sort > combined-data/test/GENE.eval
    cp original-data/test/test.in combined-data/test/

    mkdir -p combined-data/standoff/{train,devel,test}
    python tools/bc2gm2ann.py combined-data/train/{train.in,GENE.eval} combined-data/standoff/train/
    tools/bc2gm2ann.py combined-data/test/{test.in,GENE.eval} combined-data/standoff/test/

    for f in standoff/devel/*; do mv combined-data/standoff/train/`basename $f` combined-data/standoff/devel/; done
