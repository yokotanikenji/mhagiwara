#! /usr/bin/env python
# -*- coding: utf-8 -*-

# 
# Baidu Mobile Corpus usage sample script (synonym aquisition)
# 
# Copyright (c) 2010 Baidu Japan, Inc.
# URL: http://www.baidu.jp/unlp/
#
# Usage: python bmc_sample.py <2gm file> <word>
# 

import sys
import re
import math
import codecs

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

from collections import defaultdict

if len(sys.argv) != 3:
    print >>sys.stderr, "Usage: bmc_sample.py <2gm file> <word>"
    exit(1)

bgm_fn = sys.argv[1]                         # 2gm filename
word = sys.argv[2].decode('utf-8')           # query word

w2c = defaultdict(lambda: defaultdict(int))  # word to context vector
c2w = defaultdict(set)                       # context to word set (for inverted lookup)
c2i = {}                                     # context to index lookup
i2c = {}                                     # context index to string 

stopcontexts = [u"<S>", u"</S>", u"<UNK>"]

jp_codepoint = re.compile(u"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u34BF\u4E00-\u9FFF\uF900-\uFAFF]{2,}")

# read bigram file
for line in open(bgm_fn):
    bgm_str, c_str = line.decode('utf-8').split('\t')
    w1, w2 = bgm_str.split(' ')
    c = int(c_str[:-1])
    
    # w1=word, w2=context
    if not w2 in stopcontexts and jp_codepoint.match(w2):
        cr = c2i.setdefault("R:"+w2, len(c2i))
        i2c[cr] = "R:"+w2
        w2c[w1][cr] = c
        c2w[cr].add(w1)

    # w2=word, w1=context
    if not w1 in stopcontexts and jp_codepoint.match(w1):
        cl = c2i.setdefault("L:"+w1, len(c2i))
        i2c[cl] = "L:"+w1
        w2c[w2][cl] = c
        c2w[cl].add(w2)

# calc iwf (inverted word frequency; like idf)
wsum = len(w2c)
iwf = dict((c,  math.log(1.0*wsum / len(val))) for c, val in c2w.iteritems())

# list up candidates
cands = reduce(lambda x,y: x|y, [c2w[c] for c in w2c[word]])
cands.discard(word)

# calc similarity
sims = {}
veci = w2c[word]
veci_sum = sum(veci[c]*iwf[c] for c in veci)

for cand in cands:

    vecj = w2c[cand]
    vecj_sum = sum(vecj[c]*iwf[c] for c in vecj)
    num = 0.0
    for c in veci:
        if c in vecj:
            num += min(veci[c], vecj[c])*iwf[c]
    sim = num / (veci_sum + vecj_sum - num)
    sims[cand] = sim

# show results

for cand in sorted(sims, key=lambda cand: -sims[cand])[0:10]:

    cs = {}
    vecj = w2c[cand]
    for c in veci:
        if c in vecj:
            cs[c] = min(veci[c], vecj[c])*iwf[c]
    cstr = ' '.join(i2c[c] for c in sorted(cs, key=lambda c: -cs[c])[0:10])

    print "%s\t%f\t(%s)" % (cand, sims[cand], cstr)
