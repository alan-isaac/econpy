'''
Unit tests for utilities.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

import collections, random, unittest
from typing import Callable, Sequence
Function = Callable

import numpy as np

#import matplotlib.pyplot as plt

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.pytrix.utilities import n_each_rand, permutations, permutationsg
from econpy.pytrix.utilities import cumsum, cumprod, unique
from econpy.pytrix.utilities import gini, ginis, alt_gini #the main ones
from econpy.pytrix.utilities import py_gini, py_gini, py_gini2
from econpy.abm.utilities import gini2shares, gini2sharesPareto
from econpy.pytrix import fmath
from econpy.pytrix import stat



class testUtilities(unittest.TestCase):
    def setUp(self):
        self.N = 5
        self.wealths = [random.random() for _ in range(2*self.N)]
    def test_n_each_rand(self):
        n = random.randrange(500)
        TF = n_each_rand(n, (True,False))
        TFlist = list(TF)
        nT = TFlist.count(True)
        nF = TFlist.count(False)
        self.assertEqual(n, nT)
        self.assertEqual(n, nF)
        #print "n_each", n, nT, nF
    """
    def test_gini2sharesvals(self):
        gini0 = random.random()
        nbrackets = random.randrange(5,500)
        shares = gini2shares(gini=gini0, nbrackets=nbrackets)
        shares02 = gini2shares02(gini=gini0, nbrackets=nbrackets)
        self.assertEqual(list(shares),list(shares02))
    """
    def test_gini2shares(self):
        gini0 = random.random()
        nbrackets = 10**random.randrange(3,5)
        shares01 = list(gini2shares(gini=gini0, nbrackets=nbrackets))
        print("sum", sum(shares01))
        gini1 = py_gini(shares01)
        #print "ginis:", gini0, gini1   TODO: better accuracy expected...
        self.assertTrue(fmath.feq(gini0, gini1, 1e-3)) #imposed and computed Gini shd be equal
        print("here")
        shares02 = list( gini2sharesPareto(gini=gini0, nbrackets=nbrackets) )
        print("sum", sum(shares02))
        gini2 = py_gini(shares02)
        #print "ginis:", gini0, gini1   TODO: better accuracy expected...
        self.assertTrue(fmath.feq(gini0, gini2, 1./nbrackets)) #imposed and computed Gini shd be equal
        """
        print shares01[::100]
        print py_gini(shares01)
        print shares02[::100]
        print py_gini(shares02)
        fig, (ax1,ax2) = plt.subplots(1,2)
        ax1.plot(shares01)
        ax2.plot(np.cumsum(shares01))
        ax2.plot(np.cumsum(shares02))
        plt.show()
        exit()
        """
    def test_cumreduce(self):
        self.assertEqual([0,1,3,6,10],cumsum(range(5)))
        self.assertEqual([0,0,0,0,0],cumprod(range(5)))
    def test_permutations(self):
        x = permutations([1,2])
        y = permutations([0,1,2])
        z = list( permutationsg([0,1,2]) )
        self.assertEqual(x,[[1,2],[2,1]])
        self.assertEqual(y,z)
    def test_math(self):
        print(fmath.get_float_radix())
        print(fmath.get_machine_precision())
        print(fmath.get_default_numerical_precision())
        print(fmath.feq(1,2), fmath.feq(1e-9, 1e-10), fmath.feq(1e-16, 1e-17))


class testGinis(unittest.TestCase):
    def setUp(self):
        self.N = 5
        self.wealths = [10*random.random() for _ in range(2*self.N)]
        self.wealths02 = self.wealths[:]
        self.wealths02[-1] = np.nan
    def test_ginis(self):
        #test that two Gini formulae give same result
        g0 = gini(self.wealths)
        g1 = py_gini(self.wealths)
        g2 = py_gini2(self.wealths)
        g3 = alt_gini(self.wealths)
        g5, bad = ginis([self.wealths,self.wealths02])
        #print "g1:%f, g2:%f"%(g1, g2)
        for gi in (g1,g2,g3,g5):
            self.assertTrue(fmath.feq(g0,gi))
        print("g1={},g5={}, bad={}".format(g1, g5, bad))
    def test_unique(self):
        xs = list(random.randrange(10) for _ in range(20))
        us01 = unique(xs)
        us02 = list(np.unique(xs))
        self.assertEqual(us01,us02)
        us01 = unique(xs, reverse=True)
        us02 = list(reversed(np.unique(xs)))
        self.assertEqual(us01,us02)

#BEGIN:ecdf;
def simplest_ecdf(
    xs: Sequence #real numbers (the data)
    ) -> Function: #the empirical cdf of xs
    nobs = float(len(xs))
    def f(x): #the ecdf for the xs
        return sum(1 for xi in xs if xi <= x) / nobs
    return f
#END:ecdf;

def ecdf_np(
    xs: Sequence #real numbers (the data)
    ) -> Function: #the empirical cdf of xs
    xs = np.sort(xs)
    nobs = float(len(xs))
    def f(x): #the ecdf for the xs
        # side='right' to get all xi in xs if xi <= x
        return np.searchsorted(xs, x, side='right') / nobs
    return f

#chkchkchk compare to
#from statsmodels.distributions.empirical_distribution import ECDF
class testStatUtilities(unittest.TestCase):
    def test_ecdf(self):
        nobs = 100
        data = np.random.randint(100, size=(nobs,))
        cts = collections.Counter(data)
        f1 = simplest_ecdf(data)
        f2 = stat.ecdf(sorted(data))
        f3 = ecdf_np(data)

        for x in cts:
            self.assertAlmostEqual(f1(x), f2(x))
            self.assertAlmostEqual(f1(x), f3(x))



if __name__=="__main__":
    unittest.main()


# vim: set expandtab:ts=4:sw=4
