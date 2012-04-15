#!/usr/bin/env python3
# coding: utf-8

from domain import *


greek_forms = Rel()
greek_forms.load_cols("forms.txt", ("form", "pos", "parse", "lemma"))


greek_forms.query(
    PartCount(TENSE),
    PartCount(TENSE, given=INFINITIVE),
    PartCount(LIST(TENSE, VOICE), given=INFINITIVE),
    EndingTree(given=INFINITIVE),
    EndingTree(given=ALL(INFINITIVE, VOICE_IS("A"))),
    PartCount(LIST(TENSE, VOICE), given=AND(INFINITIVE, ENDS_IN("ειν"))),
    CrossTab(CASE_IS("N"), ENDS_IN("ος"), given=NOMINAL),
    Assert(ENDS_IN("ν"), given=TVM_IS("PAN"), display=LEMMA),
    Assert(ENDS_IN("ν"), given=TVM_IS("PAN"), display=LAST_3, uniq=True),
)
