import unicodedata

from qmorph import *


def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


## PROPERTIES


POS = FIELD("pos")
PARSE = FIELD("parse")
FORM = FIELD("form")
LEMMA = FIELD("lemma")


def LAST_2(t):
    "ending"
    return strip_accents(t["form"])[-2:]


def LAST_3(t):
    "ending"
    return strip_accents(t["form"])[-3:]


def CNG(t):
    "case/number/gender"
    return t["parse"][4:7]


def TVM(t):
    "tense/voice/mood"
    return t["parse"][1:4]


def TENSE(t):
    "tense"
    return t["parse"][1]


def VOICE(t):
    "voice"
    return t["parse"][2]


def MOOD(t):
    "mood"
    return t["parse"][3]


def DEGREE(t):
    "degree"
    return t["parse"][7]


def CASE(t):
    "case"
    return t["parse"][4]


def CASE_NUM(t):
    "case/number"
    return t["parse"][4:6]


def NUMBER(t):
    "number"
    return t["parse"][5]


def PERSON(t):
    "person"
    return t["parse"][0]


def TAGS(t):
    "tags"
    return " ".join(t["tags"])


## CHARACTERISTICS

# a "characteristic" is a function that takes a "tuple" and returns a boolean 
# as to whether that tuple has a particular characteristic.


def NOMINAL(t):
    "nominal"
    return t["pos"][0] in ["N", "A", "R"] or (t["pos"] == "V-" and t["parse"][3] == "P")


def INFINITIVE(t):
    "infinitive"
    return MOOD(t) == "N"


## A higher-order characteristic function is a function that returns a new
## characteristic function


def ENDS_IN(ending):
    def _(t):
        return strip_accents(t["form"]).endswith(ending)
    _.__doc__ = "-{0}".format(ending)
    return _


def TAGGED(tag):
    def _(t):
        return tag in t.tags
    _.__doc__ = "tagged {0}".format(tag)
    return _


def CNG_IS(cng):
    def _(t):
        return CNG(t) == cng
    _.__doc__ = cng
    return _


def TVM_IS(tvm):
    def _(t):
        return TVM(t) == tvm
    _.__doc__ = tvm
    return _


def CASE_IS(case):
    def _(t):
        return CASE(t) == case
    _.__doc__ = "case {0}".format(case)
    return _


def CASE_NUM_IS(case_num):
    def _(t):
        return CASE_NUM(t) == case_num
    _.__doc__ = case_num
    return _


def POS_IS(pos):
    def _(t):
        return POS(t) == pos
    _.__doc__ = pos
    return _


def PERSON_IS(person):
    def _(t):
        return PERSON(t) == str(person)
    _.__doc__ = "person {0}".format(person)
    return _


def MOOD_IS(mood):
    def _(t):
        return MOOD(t) == str(mood)
    _.__doc__ = "mood {0}".format(mood)
    return _


def VOICE_IS(voice):
    def _(t):
        return VOICE(t) == str(voice)
    _.__doc__ = "voice {0}".format(voice)
    return _


def DEGREE_IS(degree):
    def _(t):
        return DEGREE(t) == str(degree)
    _.__doc__ = "degree {0}".format(degree)
    return _


def PERSON_NUMBER_IS(person_number):
    def _(t):
        return PERSON(t) + NUMBER(t) == person_number
    _.__doc__ = "person/number {0}".format(person_number)
    return _


def STEM_SUFFIX(stem_name, ending):
    def _(t):
        if hasattr(t, stem_name):
            return strip_accents(t["form"]) == strip_accents(getattr(t, stem_name) + u(ending))
        else:
            return False
    _.__doc__ = "{0}+{1}".format(stem_name, ending)
    return _


## query classes


class EndingTree:
    
    def __init__(self, given=TRUE, limit=3):
        self.given = given
        self.limit = limit
        self.root = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    def process(self, t):
        if self.given(t):
            a, p, u = ("###" + strip_accents(t["form"]))[-3:]
            self.root[u][p][a] += 1
    
    def result(self):
        print()
        print("=========================================")
        print("Ending Tree given {0}".format(self.given.__doc__))
        print("=========================================")
        for u in self.root:
            print("{0:>20} {1}".format("-" + u, sum(sum(self.root[u][p][a] for a in self.root[u][p]) for p in self.root[u])))
            if self.limit == 1:
                continue
            for p in self.root[u]:
                print("{0:>20}   {1}".format("-" + p + u, sum(self.root[u][p][a] for a in self.root[u][p])))
                if self.limit == 2:
                    continue
                for a in self.root[u][p]:
                    print("{0:>20}     {1}".format("-" + a + p + u, self.root[u][p][a]))
        print("=========================================")
