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

## CoNLL data

The standoff was converted into a CoNLL-like format using

    https://github.com/spyysalo/standoff2conll

with

    mkdir conll
    for s in train devel test; do
        standoff2conll.py -n standoff/$s > conll/$s.tsv; done
    done

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

Two versions in CoNLL-like format were created using standoff2conll: a
"wide" version where overlapping annotations with longer spans were
kept and shorter ones discarded, and a "narrow" version where shorter
were kept and longer discarded:

    mkdir combined-data/conll-{wide,narrow}
    for s in train devel test; do
        standoff2conll.py -n -o keep-longer combined-data/standoff/$s > combined-data/conll-wide/$s.tsv;
    done
    for s in train devel test; do
        standoff2conll.py -n -o keep-shorter combined-data/standoff/$s > combined-data/conll-narrow/$s.tsv;
    done

## Train / devel split

A development set of 2500 sentences was split off from the data in the
original format with

    mkdir -p devel-split/{train,devel}
    ls standoff/devel/ | egrep '\.txt' | perl -pe 's/\.txt//' > devel.ids
    echo '^('$(tr '\n' '|' < devel.ids | perl -pe 's/\|$//')')\b' > devel.re
    egrep -f devel.re original-data/train/train.in > devel-split/devel/devel.in
    egrep -vf devel.re original-data/train/train.in > devel-split/train/train.in
    for f in {GENE,ALTGENE}.eval; do egrep -f devel.re original-data/train/$f > devel-split/devel/$f; done
    for f in {GENE,ALTGENE}.eval; do egrep -vf devel.re original-data/train/$f > devel-split/train/$f; done
