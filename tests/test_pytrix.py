'''
Unit tests for pytrix.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

import math, random, unittest
from itertools import izip
import numpy as np
import numpy.linalg as la

import simplest

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.pytrix.pytrix import Vector, Vplus, dot, norm, gcd_euclid
from econpy.pytrix.pytrix import n_take_k, factorial
from econpy.pytrix.pytrix import ordered_partitions, ordered_subpartitions
from econpy.pytrix import fmath


class testPytrix(unittest.TestCase):
    def setUp(self):
        self.list1 = range(3)
        self.list2 = [2, 4, 6]
    def test_norm(self):
        v1 = Vector(self.list1)
        n1 = np.fromiter(v1, int)
        p = random.choice([1,2,3]) 
        self.assertEqual(v1.norm(p), la.norm(n1,p))
    def test_dot(self):
        v1 = Vector(self.list1)
        v2 = Vector(self.list2)
        n1 = np.fromiter(v1, int)
        n2 = np.fromiter(v2, int)
        self.assertEqual(v1.dot(v2), np.dot(n1,n2))
    def test_vector(self):
        v1 = Vector(self.list1)
        v2 = Vector(2*x for x in self.list1)
        self.assertEqual(2*v1, v2)
        n1 = np.fromiter(v1, int)
        n2 = np.fromiter(v2, int)
        self.assertEqual(v1.dot(v2), np.dot(n1,n2))
    def test_vplus(self):
        v1 = Vplus(self.list2) #no zeros!
        v2 = Vplus(2*x for x in self.list2)
        self.assertEqual(2*v1, v2)
        mul1 = Vplus(x1*x2 for x1,x2 in izip(v1,v2))
        self.assertEqual(v1 * v2, mul1)
        div1 = Vplus(x1/x2 for x1,x2 in izip(v1,v2))
        self.assertEqual(v1 / v2, div1)
    def test_combinations(self):
        self.assertEqual(n_take_k(5,3), 10)
        self.assertEqual(n_take_k(10,3), 120)
    def test_gcd(self):
        self.assertEqual(8, gcd_euclid(8,16))
        self.assertEqual(8, gcd_euclid(-8,16))
    def test_factorial(self):
    	n = random.randint(0,10)
    	self.assertEqual(factorial(n), math.factorial(n))
    def test_ordered_partitions(self):
        self.assertEqual(ordered_partitions(2,1),[[2]])
        self.assertEqual(ordered_partitions(2,2),[[0,2],[1,1],[2,0]])
        ap22 = map(tuple,ordered_subpartitions(2,2))
        self.assertEqual(len(ap22),len(set(ap22)))
        self.assertEqual(ap22,[(0,0),(0,1),(1,0),(0,2),(1,1),(2,0)])
        nbins = random.randint(1, 9)
        n = random.randint(1, 9)
        self.assertEqual(ordered_subpartitions(0,nbins),[[0]*nbins])
        n = random.randint(1, 9)
        #the next test assumes both functions return in same order
        self.assertEqual(ordered_partitions(n,nbins), simplest.ordered_partitions(n,nbins))
        self.assertEqual(len(ordered_partitions(3,5)), 35)


'''
# tests for pnpoly
from numpy.testing import NumpyTest, NumpyTestCase
class test_poly(NumpyTestCase):
    def test_square(self):
        v = np.array([[0,0], [0,1], [1,1], [1,0]])
        assert(pnpoly(v,[0.5,0.5]))
        assert(not pnpoly(v,[-0.1,0.1]))
    def test_triangle(self):
        v = np.array([[0,0], [1,0], [0.5,0.75]])
        assert(pnpoly(v,[0.5,0.7]))
        assert(not pnpoly(v,[0.5,0.76]))
        assert(not pnpoly(v,[0.7,0.5]))
'''

if __name__=="__main__":
    unittest.main()


# vim: set expandtab:ts=4:sw=4
