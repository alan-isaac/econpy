'''
Unit tests for the `quadrature` module.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
__author__ = 'Alan G. Isaac (and others as specified)'

import unittest
from econpy.integrate import quadrature

#TODO: add tests!
# but here is a demo

f = lambda x: (x-1)*(x-1)

it = quadrature.IterativeTrapz(f, 0, 2, reportfreq=1)
it.run()
print(it.report())
