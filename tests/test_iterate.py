'''
Unit tests for the `iterate` module.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import division
import unittest
import random

import sys
sys.path.insert(0,'/econpy')  #need location of econpy
from pytrix import utilities, iterate, fmath

#simplest implementation of bisection
#BEGIN lst:optimize.bisect
def simplest_bisect(f, x1, x2):
	#comment: set small number for convergence test
	eps = 1e-8
	#require: sign change over initial interval
	if f(x1)*f(x2) > 0:
		raise ValueError
	#compute: small interval containing zero
	while abs(x1-x2) > eps:
		midpt = (x1+x2)/2
		if f(midpt)*f(x1) > 0:
			x1 = midpt
		else:
			x2 = midpt
	return (x1+x2)/2
#END lst:optimize.bisect

class Iterator4Test:
	def initialize(self):
		pass
	def iterate(self):
		pass


class test_iter(unittest.TestCase):
	def test_IterativeProcess(self):
		N = random.randrange(100)
		crit = lambda x,y: y>=N
		it = Iterator4Test()
		ip = iterate.IterativeProcess(it, crit)
		ip.run()
		self.assertEqual(ip.iterations,N)
	def test_bisect(self):
		x_int = random.randrange(20)
		f = lambda x: (x-x_int)**3
		itr = iterate.Bisect(f, x_int-1.0, x_int+1.0)
		crit = iterate.AbsDiff(1e-9)
		ip = iterate.IterativeProcess(itr, crit)
		ip.run()
		x1, x2 = itr.get_testvals()
		result1 = (x1+x2)/2
		result2 = iterate.bisect(f,  x_int-1.0, x_int+1.0, eps=1e-9)
		result3 = simplest_bisect(f, x_int-1.0, x_int+1.0)
		print "testvals", (x1,x2), result1
		print "simple bisect", result2
		print "simplest bisect", result3
		self.assert_(fmath.feq(result1, result2, 1e-7))
		self.assert_(fmath.feq(result1, result3, 1e-7))

if __name__=="__main__":
	unittest.main()

