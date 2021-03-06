"""
First Order Conventional Fuzzy Time Series by Chen (1996)

S.-M. Chen, “Forecasting enrollments based on fuzzy time series,” Fuzzy Sets Syst., vol. 81, no. 3, pp. 311–319, 1996.
"""

import numpy as np
from pyFTS.common import FuzzySet, FLR, fts, flrg


class ConventionalFLRG(flrg.FLRG):
    """First Order Conventional Fuzzy Logical Relationship Group"""
    def __init__(self, LHS, **kwargs):
        super(ConventionalFLRG, self).__init__(1, **kwargs)
        self.LHS = LHS
        self.RHS = set()

    def get_key(self, sets):
        return sets[self.LHS].name

    def append_rhs(self, c, **kwargs):
        self.RHS.add(c)

    def __str__(self):
        tmp = str(self.LHS) + " -> "
        tmp2 = ""
        for c in sorted(self.RHS, key=lambda s: s):
            if len(tmp2) > 0:
                tmp2 = tmp2 + ","
            tmp2 = tmp2 + str(c)
        return tmp + tmp2


class ConventionalFTS(fts.FTS):
    """Conventional Fuzzy Time Series"""
    def __init__(self, **kwargs):
        super(ConventionalFTS, self).__init__(order=1, **kwargs)
        self.name = "Conventional FTS"
        self.detail = "Chen"
        self.shortname = "CFTS"
        self.flrgs = {}

    def generate_flrg(self, flrs):
        for flr in flrs:
            if flr.LHS in self.flrgs:
                self.flrgs[flr.LHS].append_rhs(flr.RHS)
            else:
                self.flrgs[flr.LHS] = ConventionalFLRG(flr.LHS)
                self.flrgs[flr.LHS].append_rhs(flr.RHS)

    def train(self, data, **kwargs):

        tmpdata = FuzzySet.fuzzyfy(data, partitioner=self.partitioner, method='maximum', mode='sets')
        flrs = FLR.generate_non_recurrent_flrs(tmpdata)
        self.generate_flrg(flrs)

    def forecast(self, ndata, **kwargs):

        l = len(ndata)

        ret = []

        for k in np.arange(0, l):

            mv = FuzzySet.fuzzyfy_instance(ndata[k], self.sets)

            actual = FuzzySet.get_maximum_membership_fuzzyset(ndata[k], self.sets) #self.sets[np.argwhere(mv == max(mv))[0, 0]]

            if actual.name not in self.flrgs:
                ret.append(actual.centroid)
            else:
                _flrg = self.flrgs[actual.name]

                ret.append(_flrg.get_midpoint(self.sets))

        return ret
