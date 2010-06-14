#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re

#
# Ruby/Romkan - a Romaji <-> Kana conversion library for Ruby.
#
# Copyright (C) 2001 Satoru Takabayashi <satoru@namazu.org>
#     All rights reserved.
#     This is free software with ABSOLUTELY NO WARRANTY.
#
# You can redistribute it and/or modify it under the terms of 
# the Ruby's licence.
#
# NOTE: Ruby/Romkan can work only with EUC_JP encoding. ($KCODE="e")
#

# This table is imported from KAKASI <http://kakasi.namazu.org/> and modified.

def pairs(arr, size=2):
    for i in range(0, len(arr)-1, size):
        yield arr[i:i+size]

KUNREITAB = u"""ぁ	xa	あ	a	ぃ	xi	い	i	ぅ	xu
う	u	う゛	vu	う゛ぁ	va	う゛ぃ	vi 	う゛ぇ	ve
う゛ぉ	vo	ぇ	xe	え	e	ぉ	xo	お	o 

か	ka	が	ga	き	ki	きゃ	kya	きゅ	kyu 
きょ	kyo	ぎ	gi	ぎゃ	gya	ぎゅ	gyu	ぎょ	gyo 
く	ku	ぐ	gu	け	ke	げ	ge	こ	ko
ご	go 

さ	sa	ざ	za	し	si	しゃ	sya	しゅ	syu 
しょ	syo	じ	zi	じゃ	zya	じゅ	zyu	じょ	zyo 
す	su	ず	zu	せ	se	ぜ	ze	そ	so
ぞ	zo 

た	ta	だ	da	ち	ti	ちゃ	tya	ちゅ	tyu 
ちょ	tyo	ぢ	di	ぢゃ	dya	ぢゅ	dyu	ぢょ	dyo 

っ	xtu 
っう゛	vvu	っう゛ぁ	vva	っう゛ぃ	vvi 
っう゛ぇ	vve	っう゛ぉ	vvo 
っか	kka	っが	gga	っき	kki	っきゃ	kkya 
っきゅ	kkyu	っきょ	kkyo	っぎ	ggi	っぎゃ	ggya 
っぎゅ	ggyu	っぎょ	ggyo	っく	kku	っぐ	ggu 
っけ	kke	っげ	gge	っこ	kko	っご	ggo	っさ	ssa 
っざ	zza	っし	ssi	っしゃ	ssya 
っしゅ	ssyu	っしょ	ssho 
っじ	zzi	っじゃ	zzya	っじゅ	zzyu	っじょ	zzyo 
っす	ssu	っず	zzu	っせ	sse	っぜ	zze	っそ	sso 
っぞ	zzo	った	tta	っだ	dda	っち	tti 
っちゃ	ttya	っちゅ	ttyu	っちょ	ttyo	っぢ	ddi 
っぢゃ	ddya	っぢゅ	ddyu	っぢょ	ddyo	っつ	ttu 
っづ	ddu	って	tte	っで	dde	っと	tto	っど	ddo 
っは	hha	っば	bba	っぱ	ppa	っひ	hhi 
っひゃ	hhya	っひゅ	hhyu	っひょ	hhyo	っび	bbi 
っびゃ	bbya	っびゅ	bbyu	っびょ	bbyo	っぴ	ppi 
っぴゃ	ppya	っぴゅ	ppyu	っぴょ	ppyo	っふ	hhu 
っふぁ	ffa	っふぃ	ffi	っふぇ	ffe	っふぉ	ffo 
っぶ	bbu	っぷ	ppu	っへ	hhe	っべ	bbe	っぺ    ppe
っほ	hho	っぼ	bbo	っぽ	ppo	っや	yya	っゆ	yyu 
っよ	yyo	っら	rra	っり	rri	っりゃ	rrya 
っりゅ	rryu	っりょ	rryo	っる	rru	っれ	rre 
っろ	rro 

つ	tu	づ	du	て	te	で	de	と	to
ど	do 

な	na	に	ni	にゃ	nya	にゅ	nyu	にょ	nyo 
ぬ	nu	ね	ne	の	no 

は	ha	ば	ba	ぱ	pa	ひ	hi	ひゃ	hya 
ひゅ	hyu	ひょ	hyo	び	bi	びゃ	bya	びゅ	byu 
びょ	byo	ぴ	pi	ぴゃ	pya	ぴゅ	pyu	ぴょ	pyo 
ふ	hu	ふぁ	fa	ふぃ	fi	ふぇ	fe	ふぉ	fo 
ぶ	bu	ぷ	pu	へ	he	べ	be	ぺ	pe
ほ	ho	ぼ	bo	ぽ	po 

ま	ma	み	mi	みゃ	mya	みゅ	myu	みょ	myo 
む	mu	め	me	も	mo 

ゃ	xya	や	ya	ゅ	xyu	ゆ	yu	ょ	xyo
よ	yo

ら	ra	り	ri	りゃ	rya	りゅ	ryu	りょ	ryo 
る	ru	れ	re	ろ	ro 

ゎ	xwa	わ	wa	ゐ	wi	ゑ	we
を	wo	ん	n 

ん     n'
でぃ   dyi
ー     -
ちぇ    tye
っちぇ	ttye
じぇ	zye
"""

HEPBURNTAB = u"""ぁ	xa	あ	a	ぃ	xi	い	i	ぅ	xu
う	u	う゛	vu	う゛ぁ	va	う゛ぃ	vi	う゛ぇ	ve
う゛ぉ	vo	ぇ	xe	え	e	ぉ	xo	お	o
	

か	ka	が	ga	き	ki	きゃ	kya	きゅ	kyu
きょ	kyo	ぎ	gi	ぎゃ	gya	ぎゅ	gyu	ぎょ	gyo
く	ku	ぐ	gu	け	ke	げ	ge	こ	ko
ご	go	

さ	sa	ざ	za	し	shi	しゃ	sha	しゅ	shu
しょ	sho	じ	ji	じゃ	ja	じゅ	ju	じょ	jo
す	su	ず	zu	せ	se	ぜ	ze	そ	so
ぞ	zo

た	ta	だ	da	ち	chi	ちゃ	cha	ちゅ	chu
ちょ	cho	ぢ	di	ぢゃ	dya	ぢゅ	dyu	ぢょ	dyo

っ	xtsu	
っう゛	vvu	っう゛ぁ	vva	っう゛ぃ	vvi	
っう゛ぇ	vve	っう゛ぉ	vvo	
っか	kka	っが	gga	っき	kki	っきゃ	kkya	
っきゅ	kkyu	っきょ	kkyo	っぎ	ggi	っぎゃ	ggya	
っぎゅ	ggyu	っぎょ	ggyo	っく	kku	っぐ	ggu	
っけ	kke	っげ	gge	っこ	kko	っご	ggo	っさ	ssa
っざ	zza	っし	sshi	っしゃ	ssha	
っしゅ	sshu	っしょ	ssho	
っじ	jji	っじゃ	jja	っじゅ	jju	っじょ	jjo	
っす	ssu	っず	zzu	っせ	sse	っぜ	zze	っそ	sso
っぞ	zzo	った	tta	っだ	dda	っち	cchi	
っちゃ	ccha	っちゅ	cchu	っちょ	ccho	っぢ	ddi	
っぢゃ	ddya	っぢゅ	ddyu	っぢょ	ddyo	っつ	ttsu	
っづ	ddu	って	tte	っで	dde	っと	tto	っど	ddo
っは	hha	っば	bba	っぱ	ppa	っひ	hhi	
っひゃ	hhya	っひゅ	hhyu	っひょ	hhyo	っび	bbi	
っびゃ	bbya	っびゅ	bbyu	っびょ	bbyo	っぴ	ppi	
っぴゃ	ppya	っぴゅ	ppyu	っぴょ	ppyo	っふ	ffu	
っふぁ	ffa	っふぃ	ffi	っふぇ	ffe	っふぉ	ffo	
っぶ	bbu	っぷ	ppu	っへ	hhe	っべ	bbe	っぺ	ppe
っほ	hho	っぼ	bbo	っぽ	ppo	っや	yya	っゆ	yyu
っよ	yyo	っら	rra	っり	rri	っりゃ	rrya	
っりゅ	rryu	っりょ	rryo	っる	rru	っれ	rre	
っろ	rro	

つ	tsu	づ	du	て	te	で	de	と	to
ど	do	

な	na	に	ni	にゃ	nya	にゅ	nyu	にょ	nyo
ぬ	nu	ね	ne	の	no	

は	ha	ば	ba	ぱ	pa	ひ	hi	ひゃ	hya
ひゅ	hyu	ひょ	hyo	び	bi	びゃ	bya	びゅ	byu
びょ	byo	ぴ	pi	ぴゃ	pya	ぴゅ	pyu	ぴょ	pyo
ふ	fu	ふぁ	fa	ふぃ	fi	ふぇ	fe	ふぉ	fo
ぶ	bu	ぷ	pu	へ	he	べ	be	ぺ	pe
ほ	ho	ぼ	bo	ぽ	po	

ま	ma	み	mi	みゃ	mya	みゅ	myu	みょ	myo
む	mu	め	me	も	mo

ゃ	xya	や	ya	ゅ	xyu	ゆ	yu	ょ	xyo
よ	yo	

ら	ra	り	ri	りゃ	rya	りゅ	ryu	りょ	ryo
る	ru	れ	re	ろ	ro	

ゎ	xwa	わ	wa	ゐ	wi	ゑ	we
を	wo	ん	n	

ん     n'
でぃ   dyi
ー     -
ちぇ    che
っちぇ	cche
じぇ	je"""

KANROM = {}
ROMKAN = {}

for pair in pairs(re.split("\s+", KUNREITAB + HEPBURNTAB)):
    kana, roma = pair
    KANROM[kana] = roma
    ROMKAN[roma] = kana

# Sort in long order so that a longer Romaji sequence precedes.

_len_cmp = lambda x: -len(x)
ROMPAT = re.compile("|".join(sorted(ROMKAN.keys(), key=_len_cmp)) )

_kanpat_cmp = lambda x, y: cmp(len(y), len(x)) or cmp(len(KANROM[x]), len(KANROM[x]))
KANPAT = re.compile( u"|".join(sorted(KANROM.keys(), cmp=_kanpat_cmp )) )

KUNREI = [y for (x, y) in pairs(re.split("\s+", KUNREITAB)) ]
HEPBURN = [y for (x, y) in pairs(re.split("\s+", HEPBURNTAB) )]

KUNPAT = re.compile( u"|".join(sorted(KUNREI, key=_len_cmp)) )
HEPPAT = re.compile( u"|".join(sorted(HEPBURN, key=_len_cmp)) )

TO_HEPBURN = {}
TO_KUNREI =  {}

for kun, hep in zip(KUNREI, HEPBURN):
    TO_HEPBURN[kun] = hep
    TO_KUNREI[hep] = kun

def normalize_double_n(str):
    str = re.sub("nn", "n'", str)
    str = re.sub("n'(?=[^aiueoyn]|$)", "n", str)
    return str

def to_kana(str):
    tmp = normalize_double_n(str)
    tmp = ROMPAT.sub(lambda x: ROMKAN[x.group(0)], tmp)
    return tmp

def to_hepburn(str):
    tmp = normalize_double_n(str)
    tmp = KUNPAT.sub(lambda x: TO_HEPBURN[x.group(0)], tmp)
    return tmp

def to_kunrei(str):
    tmp = normalize_double_n(str)
    tmp = HEPPAT.sub(lambda x: TO_KUNREI[x.group(0)], tmp)
    return tmp

def to_roma(str):
    tmp = KANPAT.sub(lambda x: KANROM[x.group(0)], str)
    tmp = re.sub("n'(?=[^aeiuoyn]|$)", "n", tmp)
    return tmp

def is_consonant(str):
    return re.match("[ckgszjtdhfpbmyrwxn]", str)

def is_vowel(str):
    return re.match("[aeiou]", str)

# `z' => (za ze zi zo zu)
def expand_consonant(str):
    return [x for x in ROMKAN.keys() if re.match("^%s.$"%str, x)]

if __name__ == '__main__':
    assert to_kana("kanji") == u"かんじ"
    assert to_kana("kanzi") == u"かんじ"
    assert to_kana("kannji") == u"かんじ"
    assert to_kana("chie") == u"ちえ"
    assert to_kana("tie") == u"ちえ"
    assert to_kana("kyouju") == u"きょうじゅ"
    assert to_kana("syuukyou") == u"しゅうきょう"
    assert to_kana("shuukyou") == u"しゅうきょう"
    assert to_kana("saichuu") == u"さいちゅう"
    assert to_kana("saityuu") == u"さいちゅう"
    assert to_kana("cheri-") == u"ちぇりー"
    assert to_kana("tyeri-") == u"ちぇりー"
    assert to_kana("shinrai") == u"しんらい"
    assert to_kana("sinrai") == u"しんらい"
    assert to_kana("hannnou") == u"はんのう"
    assert to_kana("han'nou") == u"はんのう"

    assert to_hepburn("kannzi") == "kanji"
    assert to_hepburn("tie") == "chie"

    assert to_kunrei("kanji") == "kanzi"
    assert to_kunrei("chie") == "tie"

    assert to_kana("je") == u"じぇ"
    assert to_kana("e-jento") == u"えーじぇんと"

    assert to_roma(u"かんじ") == "kanji"
    assert to_roma(u"ちゃう") == "chau"
    assert to_roma(u"はんのう") == "han'nou"

    assert not is_consonant("a")
    assert is_consonant("k")

    assert is_vowel("a")
    assert not is_vowel("z")

    assert sorted(expand_consonant("k")) == ['ka', 'ke', 'ki', 'ko', 'ku']
    assert sorted(expand_consonant("s")) == ['sa', 'se', 'si', 'so', 'su']
    assert sorted(expand_consonant("t")) == ['ta', 'te', 'ti', 'to', 'tu']
    
    assert sorted(expand_consonant("ky")) == ['kya', 'kyo', 'kyu']
    assert sorted(expand_consonant("kk")) == ["kka", "kke", "kki", "kko", "kku"]
    assert sorted(expand_consonant("sh")) == ["sha", "shi", "sho", "shu"]
    assert sorted(expand_consonant("sy")) == ["sya", "syo", "syu"]
    assert sorted(expand_consonant("ch")) == ["cha", "che", "chi", "cho", "chu"]
