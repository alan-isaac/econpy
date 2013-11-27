'''
Statistical module to supplement SciPy.
'''
from __future__ import division, absolute_import

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac if not specified (and others as specified)'

import logging, math, random
from itertools import groupby, izip
import numpy as np
from matplotlib import pyplot as plt

from .utilities import have_numpy
try:
	import scipy as sp
	have_scipy = True
except ImportError:
	have_scipy = False


class Dstat1(object):
	'''Simple descriptive statistics: no missing value handling!

	Example use::

		dstat = Dstat1(x)
		#print descriptive statistics
		print dstat
		#get and plot empirical CDF
		plt.plot(*dstat.get_ecdf())

	References::

		http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/409413
		http://www.jennessent.com/arcview/sum_stats.htm
		http://en.wikipedia.org/wiki/Skewness
		http://en.wikipedia.org/wiki/Kurtosis

	:Ivariables:

		nobs : int
			total number of elements in the data set
		sum :  float
			sum of all values (n) in the data set
		min : number
			smallest value of the data set
		max : number
			largest value of the data set
		range : tuple
			(xmin, xmax)
		mode : list
			value(s) that appear(s) most often in the data set
		mean : float
			arithmetic average of the data set
		zscores : list
			z-scores for each data point
		median : float
			value which is in the exact middle of the data set
		m2 : float
			measure of the spread of the data set about the mean: MLE
		var : float
			measure of the spread of the data set about the mean: unbiased
		std : float
			standard deviation - measure of the dispersion of the data set based on var
		skew : float
			sample skewness
		kurtosis : float
			sample kurtosis
		jb : float
			Jarque-Bera statistic
		jbpval : float
			Jarque-Bera statistic's pvalue (Chi^2 df=2)

	:todo: allow using NumPy or not
	:todo: direct support for series objects
	:todo: add missing value handling? (but SciPy has this)
	:note: Don't plan to add: Sum Sq. Dev.
	'''
	def __init__(self, data1d, name=None, smpl=None, is_sorted=False):
		if len(data1d) is 0:
			raise ValueError('empty sample')
		self.data = data1d #no copy!
		self.is_sorted = is_sorted
		self.sorted_data = (self.data if is_sorted else None)
		self.id = id(self) #instance id
		self.name = name
		self.smpl = smpl
		#from sp.stats.stats import mean, variation, skew, kurtosis, histogram
		#storage attributes for associated properties (semi-private)
		self._nobs = None
		self._sum = None
		self._hist = None
		self._median = None
		self._mode = None
		self._zscores = None   #delay calc until needed
		self._range = None
		self.__nbins = None
		self.mean = self.sum/self.nobs
		self.m2, self.m3, self.m4 = self.get_cmoments(data1d)
		# m2 is MLE variance estimate (biased)
		# var is standard def of sample variance, not MLE estimate
		try: self.var =  self.m2*self.nobs/(self.nobs-1)
		except ZeroDivisionError: self.var = 0
		self.std =  math.sqrt(self.var) #based on sample variance
		self.skew = self.m3/math.sqrt(self.m2)**3
		self.kurtosis = self.m4/self.m2**2			#NOT kurtosis excess (=kurtosis-3)
		#Jarque-Bera: JB(X)=\frac{T}{6}\left[S^{2}(X) + \frac{[K(X)-3]^{2}}{4}\right]
		self.jb = (self.skew**2 + (self.kurtosis-3)**2/4)*self.nobs/6
		if have_scipy:
			self.jbpval = sp.stats.stats.chisqprob(self.jb,2) #check TODO
		else:
			self.jbpval = None
		self.min , self.max = self.get_range()
		#plt.figure()
		#plt.hist(data1d)
		#self.valid =      K-vector, the number of valid cases.
		#self.missing =     K-vector, the number of missing cases.
	def __str__(self):
		srep = '\n'
		if self.name:
			srep += 'Data:'.ljust(14) + self.name + '\n'
		if self.smpl:
			srep += 'Sample:'.ljust(14) + str(self.smpl) + '\n'
		srep += 'Sample Size:'.ljust(14) + str(self.nobs) + '\n\n'
		report = [
		('Mean', self.mean),
		('Variance',self.var),
		('StdDev',self.std),
		]
		report_fmt ="%+15s : %10.5f\n"
		for x in report:
			srep+=(report_fmt % x)
		srep += '\n'
		report = [
		('Maximum',self.max),
		('Minimum',self.min),
		('Median',self.median),
		('Skewness',self.skew),
		('Kurtosis',self.kurtosis),
		('Jarque-Bera',self.jb),
		]
		for x in report:
			if x[1] is not None:
				srep+=(report_fmt % x)
		srep += "%+15s : %s" % ('Mode',' '.join(["%0.2f" % x for x in self.mode]))
		return srep
	def get_nobs(self):
		if self._nobs is None:
			self._nobs = len(self.data)
		return self._nobs
	nobs = property(get_nobs,None,None,"Number of observations (length of series).")
	def get_sum(self):
		if self._sum is None:
			self._sum = float(sum(self.data))
		return self._sum
	sum = property(get_sum,None,None,"sum of series values as float")
	def get_zscores(self):
		if self._zscores is None:
			self._zscores = [(vi - self.mean)/self.std for vi in self.data]
		return self._zscores
	zscores = property(get_zscores,None,None,"z-scores for this series")
	def get_cmoments(self,data1d,m=[2,3,4]):
		cmoments=[]
		for xp in m:
			cmoments.append(sum([(x-self.mean)**xp for x in data1d])/self.nobs) 
		return tuple(cmoments)
	def get_sorted(self):    #TODO: choose whether to keep copy
		if self.sorted_data is None:
			self.sorted_data = sorted(self.data)  #copy!!
		return self.sorted_data
	def ecdf(self):
		return ecdf(self.get_sorted(), is_sorted=True)
	def ecdf_points(self, method='Hazen'):
		"""Return array, the ecdf values of the data."""
		return ecdf_points(data, method=method)
	"""
	def gen_ecdf(self):
		'''Return: empirical cdf as tuple of generators.

		:see: `get_ecdf`
		'''
		data, nobs = self.get_sorted(), self.nobs
		xsteps = ( data[(idx)//2] for idx in xrange(2*nobs) )
		psteps = ( ((i+1)//2)/float(nobs) for i in xrange(2*nobs) )
		return xsteps, psteps
	def get_ecdf(self, use_numpy=True):
		'''Return: 2-tuple of arrays,
		the sorted data values
		and corresponding "cumulative" relative frequencies.
		First point will be (xmin,0).
		Last point will be (xmax,1).

		:see: http://svn.scipy.org/svn/scipy/trunk/scipy/sandbox/dhuard/stats.py
			(for alternatives to steps).
		'''
		xsteps, psteps = self.gen_ecdf()
		if use_numpy:
			ecdf = np.fromiter(xsteps,'f'), np.fromiter(psteps,'f')
		else:
			ecdf = list(xsteps), list(psteps)
		return ecdf
	"""
	def get_median(self,data1d):
		if self._median is None:
			nobs = self.nobs
			idx = nobs//2
			data = self.get_sorted()
			if nobs%2:  #odd number of observations
				self._median = data[idx]
			else:       #even number of observations -> use midpt
				self._median = (data[idx-1] + data[idx]) / 2.0
		return self._median
	median = property(get_median,None,None,"median of series (midpt)")
	def get_range(self):
		if self._range is None:
			data = self.get_sorted()
			xmin = data[0]
			xmax = data[-1]
			self._range = xmin, xmax
		return self._range
	range = property(get_range,None,None,"range of series (xmin,xmax)")
	def get_histogram(self, nbins=10):
		'''
		3 bins:   xmin --- cut1] --- cut2] --- xmax]

		:todo: allow outlier exclusion
		:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/277600
		'''
		data = self.data
		nbins = int(nbins)   #returns a float
		assert (nbins>0) and (nbins<len(data))
		if self._hist is None or self.__nbins != nbins:
			xmin, xmax = self.get_range()
			assert (xmax>xmin)
			step = (xmax-xmin) / nbins
			bins = [ xmin + i*step for i in range(nbins+1) ]
			midpoints = [ (bins[i]+bins[i+1])/2. for i in range(nbins) ]
			bins[-1] = xmax  #ensure inclusion
			hist = dict().fromkeys(range(nbins),0)
			for xi in data:
				for i in range(nbins):
					if xi <= bins[i+1]:
						hist[i] += 1
						break
			self._hist = [ (midpoints[i],hist[i]) for i in range(nbins) ]
			self.__nbins = nbins
		return self._hist
	histogram = property(get_histogram,None,None,"histogram of series (using midpoints)")
	def get_mode(self, nbins=10):
		if self._mode is None:
			mode = []
			hist = self.get_histogram(nbins=nbins)
			maxct = 0
			for midpt, ct in hist:
				if ct > maxct:
					maxct = ct
					mode = [midpt]
				elif ct == maxct:
					mode.append(midpt)
				else:
					pass
			if maxct > 1:
				self._mode = mode
			else:
				self._mode = []
		return self._mode
	mode = property(get_mode,None,None,"modal value of series")

def welchs_approximate_ttest(n1, mean1, sem1, n2, mean2, sem2, alpha):
	'''Welch''s approximate t-test for the difference of two means of
	heteroscedasctic populations.

	:see: Biometry, Sokal and Rohlf, 3rd ed., 1995, Box 13.4

	:Parameters:
		n1 : int
			number of variates in sample 1
		n2 : int
			number of variates in sample 2
		mean1 : float
			mean of sample 1
		mean2 : float
			mean of sample 2
		sem1 : float
			standard error of mean1
		sem2 : float
			standard error of mean2
		alpha : float
			desired level of significance of test

	:Returns:
		significant : bool
			True if means are significantly different, else False
		t_s_prime : float
			t_prime value for difference of means
		t_alpha_prime : float
			critical value of t_prime at given level of significance

	:author: Angus McMorland
	:license: BSD_

	.. BSD: http://www.opensource.org/licenses/bsd-license.php
	'''
	svm1 = sem1**2 * n1
	svm2 = sem2**2 * n2
	t_s_prime = (mean1 - mean2)/np.sqrt(svm1/n1+svm2/n2)
	if have_scipy:
		from scipy import stats as Sstats
		t_alpha_df1 = Sstats.t.ppf(1-alpha/2, n1 - 1)
		t_alpha_df2 = Sstats.t.ppf(1-alpha/2, n2 - 1)
		t_alpha_prime = (t_alpha_df1 * sem1**2 + t_alpha_df2 * sem2**2) / \
						(sem1**2 + sem2**2)
		return abs(t_s_prime) > t_alpha_prime, t_s_prime, t_alpha_prime



from bisect import bisect_right as insertion_index
#BEGIN ecdf
def ecdf(data, is_sorted=False):
	"""Return function, the empirical cdf of `data`.
	"""
	if not is_sorted:
		data = sorted(data)
	nobs = float(len(data))
	def f(x):
		return insertion_index(data, x) / nobs
	return f
#END ecdf


class EmpiricalCDF(object):
	'''Empirical cdf.
	Incomplete: just calls D. Huard's code.
	First point will be (xmin,0).
	Last point will be (xmax,1).

	:contact: aisaac AT american.edu
	'''
	def __init__(self, data, sortdata=True):
		if sortdata:
			data = np.sort(data)
		self.data = data
		self.nobs = len(data)
	def cdf(self, method='Hazen'):
		return ecdf_points(method=method)


def ecdf_points(data, method='Hazen'):
	"""Return the empirical cdf value of each sample point.
	
	Methods available (here i goes from 1 to N)
		Hazen:	   (i-0.5)/N
		Weibull:	 i/(N+1)
		Chegodayev:  (i-.3)/(N+.4)
		Cunnane:	 (i-.4)/(N+.2)
		Gringorten:  (i-.44)/(N+.12)
		California:  (i-1)/N

	:see: http://svn.scipy.org/svn/scipy/trunk/scipy/sandbox/dhuard/stats.py
	:author: David Huard
	"""
	i = np.argsort(np.argsort(data)) + 1.
	nobs = len(data)
	method = method.lower()
	if method == 'hazen':
		cdf = (i-0.5)/nobs
	elif method == 'weibull':
		cdf = i/(nobs+1.)
	elif method == 'california':
		cdf = (i-1.)/nobs
	elif method == 'chegodayev':
		cdf = (i-.3)/(nobs+.4)
	elif method == 'cunnane':
		cdf = (i-.4)/(nobs+.2)
	elif method == 'gringorten':
		cdf = (i-.44)/(nobs+.12)
	else:
		raise 'Unknown method. Choose among Weibull, Hazen, Chegodayev, Cunnane, Gringorten and California.'
	return cdf 

