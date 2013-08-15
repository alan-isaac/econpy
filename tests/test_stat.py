'''
Unit tests for the `pytrix.stat` module.

:see: http://www.scipy.org/svn/numpy/trunk/numpy/core/tests/test_umath.py for numpy testing examples
:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import division, absolute_import

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
import unittest
import numpy
import random
from econpy.pytrix import utilities, iterate, fmath
from scipy import stats as Sstats

class testDstat(numpy.testing.NumpyTestCase):
	data = numpy.random.standard_normal(30)
	def test_descriptive(self):
		from econpy.pytrix.stat import Dstat1
		x = numpy.array(self.data)
		d = Dstat1(x)
		self.assertEqual(d.nobs , x.size)
		self.assertAlmostEqual(d.sum , x.sum())
		self.assertEqual(d.min , x.min())
		self.assertEqual(d.max , x.max())
		self.assertAlmostEqual(d.mean , x.mean())
		#var: measure of the spread of the data set about the mean: unbiased
		self.assertAlmostEqual(d.m2 , numpy.var(x))
		self.assertAlmostEqual(d.std , numpy.std(x))
		#assertEqual(d.zscores , Sstats.zs(x))
		self.assertAlmostEqual(d.median , Sstats.median(x))
		'''
			#mode: value(s) that appear(s) most often in the data set
		  #range: difference between the largest and smallest value in the data set
			 m2: measure of the spread of the data set about the mean: MLE
		   std: standard deviation - measure of the dispersion of the data set based on var
		   skew: sample skewness
	   kurtosis: sample kurtosis
			 jb: Jarque-Bera statistic
		 jbpval: Jarque-Bera statistic's pvalue (Chi^2 df=2)
		'''

class testBiometry(numpy.testing.NumpyTestCase):
	def test_welchs_approximate_ttest(self):
		'''
		:author: Angus McMorland
		:license: BSD_

		.. BSD: http://www.opensource.org/licenses/bsd-license.php
		'''
		from econpy.pytrix.stat import welchs_approximate_ttest
		chimpanzees = (37, 0.115, 0.017) # n, mean, sem
		gorillas = (6, 0.511, 0.144)
		case1 = welchs_approximate_ttest(chimpanzees[0], \
									chimpanzees[1], \
									chimpanzees[2], \
									gorillas[0], \
									gorillas[1], \
									gorillas[2], \
									0.05)
		self.assertTrue( case1[0] )
		self.assertAlmostEqual( case1[1], -2.73, 2 )
		self.assertAlmostEqual( case1[2], 2.564, 2 )

		female = (10, 8.5, n.sqrt(3.6)/n.sqrt(10))
		male = (10, 4.8, n.sqrt(0.9)/n.sqrt(10))
		case2 = welchs_approximate_ttest(female[0], \
								female[1], \
								female[2], \
								male[0], \
								male[1], \
								male[2], 0.001)
		self.assertTrue( case2[0] )
		self.assertAlmostEqual( case2[1], 5.52, 2 )
		self.assertAlmostEqual( case2[2], 4.781, 2 )

if __name__ == "__main__":
    numpy.testing.NumpyTest().run()

