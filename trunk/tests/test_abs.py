'''
Unit tests for the `abs` package.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import division, absolute_import
__docformat__ = "restructuredtext en"

import  random, unittest
import numpy as np

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.pytrix.utilities import calc_gini, calc_gini2
from econpy.abm import utilities
from econpy.abm.pestieau1984oep import agents  #chk

class test_utilities(unittest.TestCase):
	wealths = [random.random() for _ in range(30)]
	indivs = [agents.PestieauIndiv(sex=x) for x in "MF"*15]
	def test_match_exclude(self):
		f = lambda x,y: x==y  #exclude if equal
		g1 = [1,2]
		g2 = [1,2,1]
		pairs = utilities.match_exclude(g1,g2,f)
		pairs.sort()
		self.assert_( pairs == [(1,2),(2,1)] )
	def testGini(self):  #TODO: move this
		gini1 = calc_gini(self.wealths)
		gini2 = calc_gini2(self.wealths)
		print "gini1:%f, gini2:%f"%(gini1, gini2)
		self.assert_( abs(gini1-gini2)<1e-8 )
	def test_gini2shares(self):
		nshares = 30
		test_gini = random.random()
		shares = list( utilities.gini2sharesPower(test_gini, 30) )
		shares02 = np.diff( np.linspace(0, 1, nshares+1)**((1+test_gini)/(1-test_gini)) )
		self.assertTrue(np.allclose(shares, shares02))
		shares_gini = calc_gini(share*100 for share in shares)
		#print test_gini, shares_gini
		#TODO: improve accuracy
		self.assert_( abs(test_gini - shares_gini ) < 1e-02 )




if __name__=="__main__":
	unittest.main()


