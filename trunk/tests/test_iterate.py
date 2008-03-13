'''
Unit tests for the `iterate` module.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import division
from __future__ import absolute_import

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
import unittest
import math, random
from econpy.pytrix import utilities, iterate, fmath

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


#Return: `p` approximate fixed point, `pseq` approximating sequence
def smallchange(p1,p2,eps=1e-6,tol=1e-6):
	abs_change = abs(p1 - p2)
	rel_change = abs_change/(abs(p2)+eps)
	return min(abs_change,rel_change)<tol

#careful: no maxiter!
#BEGIN lst:sequence.picard1
def simplest_picard(fn, p):
	while True:
		p_1, p = p, fn(p)
		if smallchange(p_1,p):
			return p
#END lst:sequence.picard1

def simple_picard(fn, p, itermax):
	for iternum in range(itermax):
		p_1, p = p, fn(p)
		if smallchange(p_1,p):
			return p
	print "Warning: convergence failed; maximum iteration reached."




# cx:sequence.picard2  class Picard in l:\pytrix\pytrix.py

class Iterator4Test(iterate.IterativeProcess):
	def iterate(self):
		pass
	def get_testval(self):
		return 1


class test_iter(unittest.TestCase):
	def test_IterativeProcess(self):
		N = random.randrange(100)
		crit = lambda x: x.iteration >= N
		ip = Iterator4Test(crit)
		ip.run()
		self.assertEqual(ip.iteration,N)
		ip = Iterator4Test(None)
		ip.run()
		self.assertEqual(ip.iteration,100)
	def test_bisect(self):
		x4zero = random.randrange(20)
		f = lambda x: (x-x4zero)**3
		crit = iterate.AbsDiff(1e-9)
		b1 = iterate.Bisect(f, x4zero - 1.0, x4zero+1.0, crit)
		b1.run()
		print b1.report()
		result1 = b1.value
		result2 = iterate.bisect(f,  x4zero - 1.0, x4zero+1.0, eps=1e-9)
		result3 = simplest_bisect(f, x4zero - 1.0, x4zero+1.0)
		print "testvals", result1
		print "simple bisect", result2
		print "simplest bisect", result3
		self.assert_(fmath.feq(result1, x4zero, 1e-8))
		self.assert_(fmath.feq(result2, x4zero, 1e-8))
		self.assert_(fmath.feq(result3, x4zero, 1e-7))
	def test_picard(self):
		f1 = lambda x: 0.5*(x+2/x)  #approx sqrt of 2
		self.assert_(fmath.feq(iterate.Picard(f1, 1, 100, tol=1e-6).fp,math.sqrt(2),1e-6))
		f2 =lambda x: math.exp(-x)
		best_result = iterate.Picard(f2, 1, 100, tol=1e-6).fp  #must match tolerance...
		result1 = simplest_picard(f2, 1)
		result2 = simple_picard(f2, 1, 100)
		self.assert_(fmath.feq(result1, best_result, 1e-6))
		self.assert_(fmath.feq(result2, best_result, 1e-6))
		#picard(lambda x: -x,1,100)

if __name__=="__main__":
	unittest.main()

