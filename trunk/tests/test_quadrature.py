'''
Unit tests for the `quadrature` module.

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
from econpy.pytrix import utilities, fmath
from econpy.integrate import quadrature

#TODO: add tests!
# but here is a demo

f = lambda x: (x-1)*(x-1)

it = quadrature.IterativeTrapz(f, 0, 2, reportfreq=1)
it.run()
print it.report()
