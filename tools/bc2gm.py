import io

from logging import warn

class FormatError(Exception):
    pass

class Annotation(object):
    def __init__(self, sentid, start, end, text):
        self.sentid = sentid
        self.start = start
        self.end = end
        self.text = text

    def verify(self, text):
        if text[self.start:self.end] != self.text:
            raise FormatError(
                'text mismatch: annotation "%s", sentence "%s"' %
                (self.text, text[self.start:self.end]))

    def to_standoff(self, idx):
        return [
            u'T%d\tGENE %d %d\t%s' %
            (idx, self.start, self.end, self.text)
        ]

class Sentence(object):
    def __init__(self, id_, text, annotations=None):
        if annotations is None:
            annotations = []
        self.id = id_
        self.text = text
        self.annotations = annotations
        self.make_offset_map()
        
    def make_offset_map(self):
        # BC2GM offsets ignore space, create mapping to direct offsets.
        self.offset_map = []
        for i, c in enumerate(self.text):
            if not c.isspace():
                self.offset_map.append(i)

    def add_annotation(self, a):
        # Map offsets to Python string slicing convention from BC2GM
        # convention that ignores space and includes end character.
        a.start = self.offset_map[a.start]
        a.end = self.offset_map[a.end]+1
        self.annotations.append(a)

    def verify_annotations(self):
        for a in self.annotations:
            a.verify(self.text)

    def to_standoff(self):
        anns = []
        for i, a in enumerate(self.annotations, start=1):
            anns.extend(a.to_standoff(i))
        return anns

# rewrites to apply to read input lines
_rewrites = {
    # errors in source data
    'P02196565T0000|162 187|translation upstream factor':
    'P02196565T0000|163 187|translation upstream factor',
    'P01655713A0294|58 58|S-deficient':
    'P01655713A0294|58 68|S-deficient',
    'P02839716A1907|32 34|E2':
    'P02839716A1907|32 33|E2',
    'P09139910A0350|197 210|2.6 kbp (pOST2)':
    'P09139910A0350|197 209|2.6 kbp (pOST2)',
}

def read_annotations(flo):
    """Read BC2GM annotations from file-like object, return list of
    Annotation objects.

    The data consists of lines with the format

        SENTID|START END|TEXT

    where SENTID is the ID of the sentence, START and END are the span
    of the annotation in the sentence, and TEXT is the annotated text.
    """
    annotations = []
    for ln, line in enumerate(flo, start=1):
        line = line.rstrip('\n')
        if line in _rewrites:
            warn('replacing "{}" with "{}"'.format(line, _rewrites[line]))
            line = _rewrites[line]
        fields = line.split('|')
        if len(fields) != 3:
            raise FormatError('expected 3 fields, got %d: %s' %
                              (len(fields), line))
        sentid, start_end, text = fields
        try:
            start, end = start_end.split(' ')
            start = int(start)
            end = int(end)
        except:
            raise FormatError('Failed to parse line %d: %s' % (ln, line))
        # BC2GM offsets ignore space, so compare without space
        nctext = ''.join(c for c in text if not c.isspace())
        if len(nctext) != end-start+1:
            raise FormatError('Text "%s" length %d, end-start (%d-%d) is %s' %
                              (nctext, len(nctext), end, start, end-start+1))
        annotations.append(Annotation(sentid, start, end, text))
    return annotations

def read_sentences(flo):
    """Read BC2GM sentence texts from file-like object, return list of
    Sentence objects.

    The format has one sentence per line with the space-separated
    fields sentence ID and text.
    """
    sentences = []
    for line in flo:
        fields = line.strip('\n').split(' ', 1)
        if len(fields) != 2:
            raise FormatError(line)
        sentid, text = fields
        sentences.append(Sentence(sentid, text))
    return sentences

def load_annotations(fn):
    with io.open(fn, encoding='utf-8') as f:
        return read_annotations(f)

def load_sentences(fn):
    with io.open(fn, encoding='utf-8') as f:
        return read_sentences(f)

def load_bc2gm(txtfn, annfn):
    """Read BC2GM corpus data from given sentence text and annotation files,
    return list of Sentence objects."""
    sentences = load_sentences(txtfn)
    annotations = load_annotations(annfn)
    sent_by_id = { s.id: s for s in sentences }
    for a in annotations:
        sent_by_id[a.sentid].add_annotation(a)
    for s in sentences:
        s.verify_annotations()
    return sentences
