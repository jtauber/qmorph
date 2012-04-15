from collections import defaultdict


class Rel:
    def __init__(self):
        self.tuples = []
        # indexes only exist for load-time joins at the moment, not queries
        self.indexes = defaultdict(dict)
    
    def add(self, data_dict, index=None, join=None):
        # before we add the given dictionary, let's join in any extra values
        if join is not None:
            for that_rel, key_mapping, mappings in join:
                other_tuple = that_rel.indexes[key_mapping[1]].get(data_dict[key_mapping[0]])
                if other_tuple is not None:
                    data_dict.update({here: other_tuple[there] for there, here in mappings})
        
        self.tuples.append(data_dict)
        
        # now index if requested
        if index is not None:
            for i in index:
                # unique indexes at the moment as they are for joins only
                self.indexes[i][data_dict[i]] = data_dict
                
    
    def load_cols(self, filename, field_tuple, index=None, join=None):
        for line in open(filename):
            self.add(dict(zip(field_tuple, line.strip().split())), index, join)
    
    def load_dict(self, filename, index=None, join=None):
        for line in open(filename):
            self.add(dict(p.split(":") for p in line.strip().split()), index, join)
            
    
    def query(self, *queries):
        for item in self.tuples:
            for query in queries:
                query.process(item)
        
        for query in queries:
            query.result()


## characteristics


def FALSE(t):
    "false"
    return False


def TRUE(t):
    "true"
    return True


## higher-order characteristics


def FIELD(N):
    def _(t):
        return t.get(N)
    _.__doc__ = N
    return _


def AND(A, B):
   def _(t):
       return A(t) and B(t)
   _.__doc__ = "and({0},{1})".format(A.__doc__, B.__doc__)
   return _


def OR(A, B):
    def _(t):
        return A(t) or B(t)
    _.__doc__ = "or({0},{1})".format(A.__doc__, B.__doc__)
    return _


def ANY(*L):
    def _(t):
        return any([i(t) for i in L])
    _.__doc__ = "any({0})".format(", ".join([i.__doc__ for i in L]))
    return _


def ALL(*L):
    def _(t):
        return all([i(t) for i in L])
    _.__doc__ = "all({0})".format(", ".join([i.__doc__ for i in L]))
    return _


def NOT(A):
    def _(t):
        return not A(t)
    _.__doc__ = "not({0})".format(A.__doc__)
    return _


def ALWAYS():
    def _(t):
        return True
    _.__doc__ = "always"
    return _


def NEVER():
    def _(t):
        return False
    _.__doc__ = "always"
    return _


def LIST(*L):
    def _(t):
        return " ".join([(i(t) if i(t) is not None else "-") for i in L])
    _.__doc__ = ", ".join([i.__doc__ for i in L])
    return _


## query classes


class Display:

    def __init__(self, display, given=TRUE, limit=None):
        self.display = display
        self.given = given
        self.limit = limit
        self.__doc__ = display.__doc__
        if given is not TRUE:
            self.__doc__ += " " + given.__doc__
        if limit is not None:
            self.__doc__ += " limit {0}".format(limit)
        self.results = []
    
    def process(self, t):
        if self.given(t):
            self.results.append(t)
    
    def result(self):
        print()
        print("=========================================")
        print(self.__doc__)
        print("=========================================")
        for t in self.results[:self.limit]:
            print(self.display(t))
        print("=========================================")
        print("{0} items".format(len(self.results)))
        print("=========================================")


class PartCount:
    
    def __init__(self, prop, given=TRUE):
        self.prop = prop
        self.given = given
        self.alt = defaultdict(int)
        if given == TRUE:
            self.__doc__ = "{0}".format(prop.__doc__,)
        else:
            self.__doc__ = "{0} given {1}".format(prop.__doc__, given.__doc__)
    
    def process(self, t):
        if self.given(t):
            self.alt[self.prop(t)] += 1
    
    def result(self):
        print()
        print("=========================================")
        print(self.__doc__)
        print("=========================================")
        for a, b in self.alt.items():
            print("{0:<20}{1:>20}".format(a, b))
        print("-----------------------------------------")
        print("partitions: {0}".format(len(self.alt)))
        print("=========================================")


class CrossTab:
    
    def __init__(self, char1, char2, given=TRUE):
        self.char1 = char1
        self.char2 = char2
        self.given = given
        self.count1 = 0
        self.count2 = 0
        self.count3 = 0
        self.count4 = 0
        if given == TRUE:
            self.__doc__ = "{0} vs {1}".format(char1.__doc__, char2.__doc__)
        else:
            self.__doc__ = "{0} vs {1} given {2}".format(char1.__doc__, char2.__doc__, given.__doc__)
    
    def process(self, t):
        if self.given(t):
            if self.char1(t):
                if self.char2(t):
                    self.count1 += 1
                else:
                    self.count2 += 1
            else:
                if self.char2(t):
                    self.count3 += 1
                else:
                    self.count4 += 1
    
    def result(self):
        print()
        print("=========================================")
        print(self.__doc__)
        print("=========================================")
        print(" {0:>20} {1:>8}".format(self.char2.__doc__, "not"))
        print("-----------------------------------------")
        print("{0:<10} | {1:>8} {2:>8} | {3:>8}".format(self.char1.__doc__, self.count1, self.count2, self.count1 + self.count2))
        print("not        | {0:>8} {1:>8} | {2:>8}".format(self.count3, self.count4, self.count3 + self.count4))
        print("-----------------------------------------")
        print("           | {0:>8} {1:>8} | {2:>8}".format(self.count1 + self.count3, self.count2 + self.count4, self.count1 + self.count2 + self.count3 + self.count4))
        print("=========================================")


class Assert:
    
    def __init__(self, assertion, display=str, given=TRUE, uniq=False):
        self.assertion = assertion
        self.display = display
        self.given = given
        self.violations = []
        self.uniq = uniq
        if given == TRUE:
            self.__doc__ = assertion.__doc__
        else:
            self.__doc__ = "{0} given {1}".format(assertion.__doc__, given.__doc__)
    
    def process(self, t):
        if self.given(t) and not self.assertion(t):
            self.violations.append(t)
    
    def result(self):
        print()
        print("=========================================")
        if not self.uniq:
            print("violations of {0}: {1}".format(self.__doc__, len(self.violations)))
            print("-----------------------------------------")
            for t in self.violations:
                print(self.display(t))
            if len(self.violations) > 10:
                print("-----------------------------------------")
                print("violations of {0}: {1}".format(self.__doc__, len(self.violations)))
        else:
            vv = defaultdict(int)
            for t in self.violations:
                vv[self.display(t)] += 1
            print("violations of {0}: {1} types {2} total".format(self.__doc__, len(vv), len(self.violations)))
            print("-----------------------------------------")
            for s, c in vv.items():
                print("{0:<20}{1:>20}".format(s, c))
        print("=========================================")
