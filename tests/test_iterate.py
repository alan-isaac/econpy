'''
Unit tests for the `iterate` module.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
#from __future__ import division
#from __future__ import absolute_import
import random
from math import sqrt, exp
from typing import Callable
from numbers import Real, Integral

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
import unittest
import math, random
from econpy.pytrix import utilities, fmath
from econpy.optimize import iterate

#BEGIN lst:optimize.bracket
def simplest_bracket(
f : Callable, #float->float (continuous function)
xa : float, #interval lower bound
xb : float, #interval upper bound
nextpoint : Callable, #(float,float,float,float)->(float,float)
reiter : Callable, #(float,float,float,float,int)->bool
) -> float: #x in (xa .. xb) s.t. f(x) approx 0
	fa, fb = f(xa), f(xb)
	ct = 0
	while reiter(xa, xb, fa, fb, ct):
		xnew = nextpoint(xa, xb, fa, fb)
		fnew = f(xnew)
		if(fnew * fa > 0):#then
			xa, fa = xnew, fnew
		else:
			xb, fb = xnew, fnew
		ct = ct + 1
	return xa if(abs(fa) < abs(fb)) else xb
#END lst:optimize.bracket

#simplest implementation of bisection
#BEGIN lst:optimize.bisect
def xmid(xa, xb, fa, fb):
	return (xa + xb) / 2.0
#END lst:optimize.bisect

#BEGIN lst:optimize.ftol
def simplest_ftol(xa, xb, fa, fb, itr):
	ftol = 1e-9
	return (abs(fa) > ftol) and (abs(fb) > ftol)
#END lst:optimize.ftol

#goal: find root by bisection
#BEGIN lst:optimize.bisection
def simplest_bisection(f, xa, xb):
	return simplest_bracket(
		f, xa, xb,
		nextpoint=xmid,
		reiter=simplest_ftol)
#END lst:optimize.bisection

def simplest_randomsection(f, xa, xb):
	return simplest_bracket(
		f, xa, xb,
		nextpoint=lambda xa, xb, fa, fb: xa + (xb-xa)*random.random(),
		reiter=simplest_ftol)


#simplest implementation of regula falsi
#BEGIN lst:optimize.falsi
def xfalse(xa, xb, fa, fb):
	lam = fb / (fb - fa)
	return lam * xa + (1 - lam) * xb

def simplest_falseposition(f, xa, xb):
	return simplest_bracket(
		f, xa, xb,
		nextpoint=xfalse,
		reiter=simplest_ftol)
#END lst:optimize.falsi

def simplest_falseposition_old(f, x1, x2):
	#comment: set small number for convergence test
	eps = 1e-8
	f1, f2 = f(x1), f(x2)
	if f1*f2 > 0:
		raise ValueError("Sign changing interval required.")
	xnew, fnew = x2, f2
	while abs(fnew) > eps:
		#compute: x such that f(x) is near 0
		lam = f2 / (f2 - f1)
		xnew = lam*x1 + (1-lam)*x2
		fnew = f(xnew)
		if fnew*f1 > 0:
			x1, f1 = xnew, fnew
		else:
			x2, f2 = xnew, fnew
	return xnew

#simplest implementation of Ridders' method
# comment: does not test midpt (natural extension)
#BEGIN lst:optimize.ridders
def simplest_ridders(f, x1, x2):
	#comment: set small number for convergence test
	eps = 1e-8
	f1, f2 = f(x1), f(x2)
	#require: sign change over initial interval
	if f1*f2 > 0:
		raise ValueError("Sign changing interval required.")
	xnew, fnew = (x2, f2) if (abs(f2)<abs(f1)) else (x1,f1)
	while abs(fnew) > eps:
		#compute: x such that f(x) is near 0
		xmid = (x1 + x2)/2.
		fmid = f(xmid)
		xnew = xmid - (x2-xmid)*fmid/sqrt(fmid*fmid-f1*f2)
		fnew = f(xnew)
		if fnew*f1 > 0:
			x1, f1 = xnew, fnew
		else:
			x2, f2 = xnew, fnew
	return xnew
#END lst:optimize.ridders




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
	print("Warning: convergence failed; maximum iteration reached.")




# cx:sequence.picard2  class Picard

class Iterator4Test(iterate.IterativeProcess):
	def iterate(self):
		pass
	def get_testval(self):
		return 1


class test_iter(unittest.TestCase):
	def test_IterativeProcess(self):
		N = random.randrange(100)
		crit = lambda x, value, iteration: x.iteration >= N
		ip = Iterator4Test(crit)
		ip.run()
		self.assertEqual(ip.iteration,N)
		ip = Iterator4Test(None)
		ip.run()
		self.assertEqual(ip.iteration,100)
	def test_bisect(self):
		print("""START TEST""")
		x4zero = random.randrange(20)
		f = lambda x: (x-x4zero)**3
		crit = iterate.AbsDiff(1e-9)
		b1 = iterate.Bisect(f, x4zero - 1.0, x4zero+1.0, crit)
		b1.run()
		#print b1.report()
		result1 = b1.value
		result2 = iterate.bisect(f,  x4zero - 1.0, x4zero+1.0, eps=1e-9)
		result3 = simplest_bisection(f, x4zero - 1.0, x4zero+1.0)
		print("testvals", b1.value)
		print("simple bisect", result2)
		print("simplest bisection", result3)
		self.assertTrue(fmath.feq(b1.value, x4zero, 1e-8))
		self.assertTrue(fmath.feq(result2, x4zero, 1e-8))
		self.assertTrue(fmath.feq(result3, x4zero, 1e-7))
	def test_falsi(self):
		x4zero = random.randrange(20)
		f = lambda x: (x-x4zero)**3
		result1 = simplest_falseposition(f,   x4zero - 1.0, x4zero+1.0)
		print("testvals", result1)
		self.assertTrue(fmath.feq(result1, x4zero, 1e-8))
	def test_ridders(self):
		shift = random.randrange(20)
		f = lambda x: x*exp(x) - shift
		testval = simplest_bisection(f,   -10., 10.)
		result1 = simplest_ridders(f,   -10., 10.)
		print("Ridders method with shift=%f"%shift)
		print("testvals", result1)
		self.assertTrue(fmath.feq(result1, testval, 1e-8))
	def test_picard(self):
		f1 = lambda x: 0.5*(x+2/x)  #approx sqrt of 2
		self.assertTrue(fmath.feq(iterate.Picard(f1, 1, 100, tol=1e-6).fp,math.sqrt(2),1e-6))
		f2 =lambda x: math.exp(-x)
		best_result = iterate.Picard(f2, 1, 100, tol=1e-6).fp  #must match tolerance...
		result1 = simplest_picard(f2, 1)
		result2 = simple_picard(f2, 1, 100)
		self.assertTrue(fmath.feq(result1, best_result, 1e-6))
		self.assertTrue(fmath.feq(result2, best_result, 1e-6))
		#picard(lambda x: -x,1,100)

if __name__=="__main__":
	unittest.main()
	#print(simplest_randomsection(lambda x: x*x*x, -10, 1))


