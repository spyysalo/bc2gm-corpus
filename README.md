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
