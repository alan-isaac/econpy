'''
Unit tests for utilities.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

import unittest
import random
import numpy

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.pytrix.utilities import n_each_rand, permutations, permutationsg
from econpy.pytrix.utilities import cumsum, cumprod
from econpy.pytrix.utilities import calc_gini, calc_gini2, calc_gini3, calc_gini4
from econpy.abs.utilities import gini2shares
from econpy.pytrix import fmath



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
	def test_gini2shares(self):
		gini0 = random.random()
		nbrackets = random.randrange(5,500)
		shares = gini2shares(gini=gini0, nbrackets=nbrackets)
		gini1 = calc_gini(shares)
		#print "ginis:", gini0, gini1   TODO: better accuracy expected...
		self.assert_(fmath.feq(gini0, gini1, 1e-3)) #imposed and computed Gini shd be equal
	def test_cumreduce(self):
		self.assertEqual([0,1,3,6,10],cumsum(range(5)))
		self.assertEqual([0,0,0,0,0],cumprod(range(5)))
	def test_permutations(self):
		x = permutations([1,2])
		y = permutations(range(3))
		z = list( permutationsg(range(3)) )
		self.assertEqual(x,[[1,2],[2,1]])
		self.assertEqual(y,z)
	def test_calc_gini(self):
		#test that two Gini formulae give same rsult
		gini1 = calc_gini(self.wealths)
		gini2 = calc_gini2(self.wealths)
		gini3 = calc_gini3(self.wealths)
		gini4 = calc_gini4(self.wealths)
		#print "gini1:%f, gini2:%f"%(gini1, gini2)
		self.assert_(fmath.feq(gini1,gini2))
		self.assert_(fmath.feq(gini1,gini3))
		print gini1, gini4
		self.assert_(fmath.feq(gini1,gini4))
	def test_math(self):
		print
		print fmath.get_float_radix()
		print fmath.get_machine_precision()
		print fmath.get_default_numerical_precision()
		print fmath.feq(1,2), fmath.feq(1e-9, 1e-10), fmath.feq(1e-16, 1e-17)

if __name__=="__main__":
	unittest.main()


