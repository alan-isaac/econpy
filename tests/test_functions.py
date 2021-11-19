'''
Unit tests for the `functions` package.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
__docformat__ = "restructuredtext en"
from typing import Any, Callable, Sequence
from numbers import Real, Integral
import operator
from functools import reduce

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
import unittest
import random
import numpy
#from econpy.functions import polyuv
from typing import Callable
from numbers import Real, Integral

#BEGIN lst:function.differenceQuotient
def simplest_differenceQuotient(
    f: Callable, #underlying function
    x: Real,     #source point
    h: Real      #step
    ) -> Real:
    df = f(x + h) - f(x) #change of value of f
    return df / h        #value of difference quotient
#END lst:function.differenceQuotient

#BEGIN lst:function.simplest_horner
#goal: evaluate polynomial at point x
#input:
#    coefficients : tuple (ordered as (a_0,...,a_N))
#    x : number (point of evaluation)
#output:
#    result : number (value of polynomial at x)
def simplest_horner(coefficients, x):
    result = 0
    for coef in reversed(coefficients):
        result = coef + result * x
    return result
#END lst:function.simplest_horner

#BEGIN lst:simplest_hornerd
#goal: evaluate polynomial p and derivative p' at point x
#input:
#    coefficients : tuple (ordered as (a_0,...,a_N))
#    x : number (point of evaluation)
#output:
#    result : number,number = p(x), p'(x)
def hornerd(coefficients, x):
    p0 = 0
    p1 = 0
    for coef in reversed(coefficients):
        p1 = p1*x + p0
        p0 = p0*x + coef
    return p0, p1
#END lst:simplest_hornerd

#BEGIN:horner
def horner(coefficients: Sequence[float], x: float):
    f = lambda acc, coef: coef + x * acc
    return reduce(f, reversed(coefficients), 0)
#END:horner

class test_functions(unittest.TestCase):
    coefficients = random.sample(range(1,20), 5)
    coefs = [1.0, 0.2, 1.0, -0.4]
    """
    def test_polyderiv(self):
        a = self.coefficients
        b = [ (i+1)*a[i+1] for i in range(len(a)-1) ]
        self.assertEqual(b, polyuv.polyderiv(a))
        c = [ (i+1)*b[i+1] for i in range(len(b)-1) ]
        self.assertEqual(c, polyuv.polyderiv(b))
        self.assertEqual(c, polyuv.polyderiv(a,d=2))
    """
    def test_horner(self):
        cs = self.coefficients
        cs1 = [ (i+1)*cs[i+1] for i in range(len(cs)-1) ]
        cs2 = [ (i+1)*cs1[i+1] for i in range(len(cs1)-1) ]
        x = random.random()
        ref0 = simplest_horner(cs, x)
        ref1 = simplest_horner(cs1,x)
        ref2 = simplest_horner(cs2,x)
        self.assertEqual(ref0, horner(cs, x) )
        self.assertEqual(ref0, hornerd(cs, x)[0] )
        self.assertAlmostEqual(ref1, hornerd(cs, x)[1] )

    """
    def test_PolynomailUV(self):
        p1 = polyuv.PolynomialUV(self.coefs)
        x = -1.9
        self.assertEqual( p1(x), ((-0.4*x + 1.0)*x + 0.2)*x + 1.0 )
    def test_deriv(self):
        coefs = range(6)
        random.shuffle(coefs)
        p = numpy.poly1d(list(reversed(coefs)))
        for n in range(len(coefs)):
            self.assertEqual(polyuv.polyderiv(coefs, n),  list(p.deriv(m=n).c)[::-1] ) 
    """
    def test_differenceQuotient(self):
        f = lambda x: x * x
        x0 = 2
        h = 1
        df = f(x0+h) - f(x0)
        self.assertEqual(5, simplest_differenceQuotient(f,x0,h))

'''
zeros = p1.zeros()
for z in zeros:
    print z, p1(z)
p2 = Polynomial([[1.,0.3],[-0.2,0.5]])
y = 0.3
print p2(x,y), 1. + 0.3*y - 0.2*x + 0.5*x*y
fit = fitPolynomial(2, [1.,2.,3.,4.], [2.,4.,8.,14.])
print fit.coeff

p = Polynomial([1., 1.])
invp = 1./p
pr = RationalFunction(p)
print pr+invp
'''



if __name__=="__main__":
    unittest.main()

# vim: set expandtab:ts=4:sw=4
