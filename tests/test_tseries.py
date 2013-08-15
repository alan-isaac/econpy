'''
Unit tests for tseries.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

from itertools import izip
import random
import numpy as np
import numpy.linalg as la
import unittest

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.pytrix.tseries import varlags
from econpy.pytrix import fmath


class testTseries(unittest.TestCase):
	def test_varlags(self):
		x = np.arange(20).reshape((10,2))
		xnew, xlags = varlags(x, 2)
		self.assert_((x[2:]==xnew).all())
		self.assert_((xlags[:,:2]==x[1:-1]).all())
		self.assert_((xlags[:,2:]==x[:-2]).all())


if __name__=="__main__":
	unittest.main()



