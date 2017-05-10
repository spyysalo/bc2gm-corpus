#!/usr/bin/env python

# Combine data with predictions for evaluation with BioCreative II
# Gene Mention (BC2GM) evaluation script.

import sys

from collections import defaultdict, OrderedDict
from itertools import chain, tee, izip

from logging import warn

# Sentence separator(s) used in predictions
SEPARATORS = ['-DOCSTART-', '-X-']

# adapted from http://docs.python.org/library/itertools.html#recipes
def pairwise(iterable, include_last=False):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    if not include_last:
        return izip(a, b)
    else:
        return izip(a, chain(b, (None, )))

def iobes_to_iob2(data):
    prev = None
    for fields in data:
        iobes = fields[-1]
        if iobes == 'O' or iobes[0] in ('B', 'I'):
            iob2 = iobes
        elif iobes[0] == 'E':
            iob2 = 'I' + iobes[1:]
        else:
            assert iobes[0] == 'S', 'invalid tag %s' % iobes
            iob2 = 'B' + iobes[1:]
        prev = iobes
        fields[-1] = iob2
    return data

def with_open(fn, func):
    if fn == '-':
        return func(sys.stdin)
    else:
        with open(fn) as f:
            return func(f)

def read_predictions(f):
    if isinstance(f, str):
        return with_open(f, read_predictions)
    sentences, current = [], []
    for line in f:
        line = line.rstrip('\n\r')            
        fields = line.split()
        if not line or fields[0] in SEPARATORS:
            sentences.append(current)
            current = []
        else:
            text, tag = fields[0], fields[-1]
            current.append([text, tag])
    sentences.append(current)
    sentences = [s for s in sentences if s]    # take out empties
    sentences = [iobes_to_iob2(s) for s in sentences]
    return sentences

def read_bc2gm_text(f):
    if isinstance(f, str):
        return with_open(f, read_bc2gm_text)
    id_and_text = []
    for line in f:
        line = line.rstrip('\n\r')
        id_, text = line.split(' ', 1)
        id_and_text.append((id_, text))
    return id_and_text

def write_bc2gm(bc2gm_fields, out=sys.stdout):
    for sentid, start, end, text in bc2gm_fields:
        out.write('{}|{} {}|{}\n'.format(sentid, start, end, text))

def split_tagged(tt):
    if tt is None:
        return (None, None)
    else:
        return tt[0], tt[1]

def split_tag(t):
    if t is None or '-' not in t:
        return t, None
    else:
        return t.split('-', 1)

def is_start(curr_start, curr_tag):
    if split_tag(curr_tag)[0] in ('B', 'S'):
        return True    # start tag
    else:
        return False

def pred_to_offsets(text_and_tags):
    offsets = []
    offset, curr_start, tokens = 0, None, None
    for curr, next_ in pairwise(text_and_tags, include_last=True):
        curr_tok, curr_tag = split_tagged(curr)
        next_tok, next_tag = split_tagged(next_)
        if is_start(curr_start, curr_tag):
            curr_start = offset
            tokens = []
        if curr_start is not None:
            tokens.append(curr_tok)
            if not (split_tag(next_tag)[0] in ('I', 'E')):    # end
                text = ' '.join(tokens)
                offsets.append((curr_start, offset+len(curr_tok)-1, text))
                curr_start, tokens = None, None
        offset += len(curr_tok)
    return offsets

def check_text(gold_text, pred_text):
    # Space is lost in tokenization, so compare without space
    if gold_text.replace(' ', '') != pred_text.replace(' ', ''):
        raise ValueError('Text mismatch: "{}" vs "{}"'.format(
            gold_text, pred_text
        ))
    return True

def texts_match(sentid_and_text, predictions):
    assert len(sentid_and_text) == len(predictions)
    for i in range(len(sentid_and_text)):
        gold_text = sentid_and_text[i][1]
        text_and_tags = predictions[i]
        pred_text = ' '.join(map(lambda t: t[0], text_and_tags))
        if gold_text.replace(' ', '') != pred_text.replace(' ', ''):
            return False
    return True

def reorder_predictions(sentid_and_text, predictions):
    assert len(sentid_and_text) == len(predictions)
    text_to_index = defaultdict(list)
    for i, (sentid, gold_text) in enumerate(sentid_and_text):
        # Map without space to accommodate tokenization differences
        chars = gold_text.replace(' ', '')
        text_to_index[chars].append(i)
    indexed_predictions = {}
    for text_and_tags in predictions:
        pred_text = ' '.join(map(lambda t: t[0], text_and_tags))
        chars = pred_text.replace(' ', '')
        if not text_to_index[chars]:
            raise ValueError('Failed to match predicted text "{}"'.format(
                pred_text))
        index = text_to_index[chars].pop(0)
        indexed_predictions[index] = text_and_tags
    reordered = [ip[1] for ip in sorted(indexed_predictions.items())]
    return reordered

def convert_to_bc2gm(sentid_and_text, predictions):
    if len(sentid_and_text) != len(predictions):
        raise ValueError('Sentence number mismatch: {} vs {}'.format(
            len(sentid_and_text), len(predictions)
        ))
    if not texts_match(sentid_and_text, predictions):
        warn('text mismatch, trying to reorder...')
        predictions = reorder_predictions(sentid_and_text, predictions)
    bc2gm_fields = []
    for i in range(len(sentid_and_text)):
        sentid, gold_text = sentid_and_text[i]
        text_and_tags = predictions[i]
        pred_text = ' '.join(map(lambda t: t[0], text_and_tags))
        pred_tags = map(lambda t: t[1], text_and_tags)
        check_text(gold_text, pred_text)
        offsets = pred_to_offsets(text_and_tags)
        bc2gm_fields.extend([(sentid,) + o for o in offsets])
    return bc2gm_fields

def main(argv):
    if len(argv) != 3:
        print >> sys.stderr, 'Usage: {} PREDICTIONS TEXT.in'.format(__file__)
        return 1
    predictions = read_predictions(argv[1])
    sentid_and_text = read_bc2gm_text(argv[2])
    bc2gm_fields = convert_to_bc2gm(sentid_and_text, predictions)
    write_bc2gm(bc2gm_fields, sys.stdout)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
