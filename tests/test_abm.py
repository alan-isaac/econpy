'''
Unit tests for the `abms` examples..

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
import operator
import  random, unittest
import numpy as np

from econpy.pytrix.utilities import gini, alt_gini
from econpy.abms import utilities
from econpy.abms.pestieau1984oep import agents  #chk

class test_utilities(unittest.TestCase):
    wealths = [random.random() for _ in range(30)]
    indivs = [agents.PestieauIndiv(sex=x) for x in "MF"*15]
    def test_match_exclude(self):
        g1 = [1,2]
        g2 = [1,2,1]
        pairs = sorted(utilities.match_exclude(g1,g2,operator.eq))
        expect = [(1,2),(2,1)] 
        msg = f"got {pairs}, expected {expect}"
        self.assertTrue( sorted(pairs) == expect, msg=msg)
    def testGini(self):  #TODO: move this
        gini1 = gini(self.wealths)
        gini2 = alt_gini(self.wealths)
        msg: str = f"gini {gini1} vs gini {gini2}"
        self.assertAlmostEqual(gini1,gini2,msg=msg)
    def test_gini2shares(self):
        nshares = 30
        test_gini = random.random()
        shares = list( utilities.gini2sharesPower(test_gini, 30) )
        shares02 = np.diff( np.linspace(0, 1, nshares+1)**((1+test_gini)/(1-test_gini)) )
        self.assertTrue(np.allclose(shares, shares02))
        shares_gini = gini([share*100 for share in shares])
        msg: str = f"test {test_gini} vs calculated shares {shares_gini}"
        self.assertTrue(abs(test_gini-shares_gini)< 1e-03,msg=msg) #TODO: improve accuracy




if __name__=="__main__":
    unittest.main()


# vim: set noet:ts=4:sw=4
