# QMORPH

**QMORPH** is a Python3 library for querying and pivoting tabular data. It was
first written a number of years ago as part of my doctoral work on Ancient
Greek morphology but has potentially broader applications. I've recently
updated it to Python 3 and will likely change some things inspired by the
Django ORM's query syntax.

## Example

```
from qmorph import *

greek_forms = Rel()
greek_forms.load_cols("forms.txt", ("form", "pos", "parse", "lemma"))

greek_forms.query(PartCount(lambda t: t.pos))
```

`Rel` initializes the relation.

`load_cols` parses a given line-per-record, whitespace-delimited file into
objects with the given fields.

`query` then runs the given query or list of queries on those objects.

`PartCount` is a provided **query class** that partitions and counts the
objects based on the given **property function**. Above the property function
is provided inline but the equivalent could be achieved using the higher-order
``FIELD`` function provided:

```
from qmorph import *

greek_forms = Rel()
greek_forms.load_cols("forms.txt", ("form", "pos", "parse", "lemma"))
greek_forms.query(PartCount(FIELD("pos")))
```

which is equivalent to our first example.

Often you end up writing your own property functions. For example, we could
write ``TENSE``, a function to extract the tense from the ``parse`` field and
then do:

```
from domain import *

greek_forms = Rel()
greek_forms.load_cols("forms.txt", ("form", "pos", "parse", "lemma"))
greek_forms.query(PartCount(TENSE))
```

resulting in output like:

```
=========================================
tense
=========================================
A                                   4106
F                                    749
I                                    525
-                                   8779
P                                   3898
Y                                     36
X                                    779
-----------------------------------------
partitions: 7
=========================================
```

`PartCount` also takes an optional `given` argument to restrict the items
considered based on the given **characteristic function**. We can define
domain-specific *characteristic functions* such as ``INFINITIVE`` and do
the following:

```
PartCount(TENSE, given=INFINITIVE),
```

which will give:

```
=========================================
tense given infinitive
=========================================
A                                    448
P                                    394
X                                     32
F                                      3
-----------------------------------------
partitions: 4
=========================================
```

*Property functions* can be combined with `LIST` so that

```
PartCount(LIST(TENSE, VOICE), given=INFINITIVE),
```

will partition the infinitives based on both `TENSE` and `VOICE`:

```
=========================================
tense, voice given infinitive
=========================================
P P                                   72
A M                                   50
X P                                    9
A A                                  310
P A                                  258
F A                                    1
X M                                    1
F M                                    2
A P                                   88
X A                                   22
P M                                   64
-----------------------------------------
partitions: 11
=========================================
```

Another *query class* is `CrossTab` which takes two *characteristic functions*
and generates a cross-table. It can also optionally be restricted to a given
*characteristic function*:

```
CrossTab(CASE("N"), ENDS_IN("ος"), given=NOMINAL),
```

Note that the *characteristic function* `NOMINAL` and higher-order
*characteristic functions* `CASE` and `ENDS_IN` are domain-specific (it's
easy to write your own as you can see below). This results in:

```
=========================================
case N vs -ος given nominal
=========================================
                  -ος      not
-----------------------------------------
case N     |      595     3508 |     4103
not        |      315     6957 |     7272
-----------------------------------------
           |      910    10465 |    11375
=========================================
```

Yet another provided *query class* is `Assert` which will identify any
violations of a particular *characteristic function*. For example, if you
want to assert that present active infinitives (domain-specific
*characteristic function* `TVM_IS("PAN")`) end in ν (domain-specific
*characteristic function* `ENDS_IN("ν")`) and show the lemmas (*property
function* `LEMMA`) of the violators, you use:

```
Assert(ENDS_IN("ν"), given=TVM_IS("PAN"), display=LEMMA),
```

It is possible to write your own *query classes*. In morphology work, for
example, I use a *query class* ``EndingTree`` to show the possible endings
a given type of word (identified by *characteristic function*) can have.

```
EndingTree(given=INFINITIVE),
```

As mentioned at the start, you can write your own *property functions*:

```
def TENSE(t):
    "tense"
    return t.parse[1]
```

which can be combined with `LIST` as we saw above in things like
`LIST(TENSE, VOICE)`.

Notice that *property functions* take an object `t` and return some string
value from that object.

You can also write your own *characteristic functions*:

```
def NOMINAL(t):
    "nominal"
    return t.pos[0] in ["N", "A", "R"] or (t.pos == "V-" and t.parse[3] == "P")
```

and *higher-order characteristic functions* (functions which return
*characteristic functions*):

```
def ENDS_IN(ending):
    def _(t):
        return strip_accents(t.form).endswith(ending)
    _.__doc__ = "-{0}".format(ending)
    return _
```

*Characteristic functions* can be combined with `AND`, `OR`, `NOT`, `ANY` and
`ALL`. There are also built-in *characteristic functions* `ALWAYS` and
`NEVER`.

Notice that *characteristic functions* take an object `t` and return a boolean
indicating whether the object has that characteristic.

Note that the doc-strings are very important as they are used as part of the
output of query results.
