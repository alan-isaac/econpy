'''Simple time series manipulations.

:note: Run as __main__ to see example use.
:author: Alan G. Isaac, except where otherwise specified.
:since: 2004-08-04
:date: 2005-08-23
:copyright: 2005 Alan G. Isaac, except where otherwise specified.
:license: `MIT license`_
:see: pytrix.py
:see: io.py
:see: pyGAUSS.py
:see: tseries.py

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
__docformat__ = "restructuredtext en"
import pytrix  #`series` subclasses `vector`
reload(pytrix)
import io
import logging
logging.getLogger().setLevel(logging.DEBUG) #sets root logger level
#see http://www.python.org/doc/2.3.5/lib/node304.html to log to a file
#(after Python 2.4 can use basicConfig)
import math
import itertools
import matplotlib
matplotlib.use('TkAgg')
import pylab
from matplotlib.dates import date2num, MONTHLY, YEARLY
import datetime
import Tkinter as Tk

have_numpy = False
try:
	import numpy as N
	have_numpy = True
except ImportError:
	logging.info("numpy not available")
have_scipy = False
try:
	import scipy
	have_scipy = True
except ImportError:
	logging.info("SciPy not available")


'''
To Do
-----

- Improve Sample class in pytrix_io
		Accept strings in Sample class args
		Support conditional Sample
		shd accept a sample and a condition as args
		Test that sample length matches data length
		use sample length to reserve space for data
- Replace pylab calls w Matplotlib calls
	get rid of show()
	add 2 scale plots
	http://matplotlib.sourceforge.net/examples/two_scales.py

Comments
--------
- uses Matplotlib's dateutil but see
  https://moin.conectiva.com.br/DateUtil

Limitations
-----------
- Assumes time series data with a stated frequency (1,4,12)

Extensions
---------- 
- Handle comment lines
	Name: 
	Display Name: 
	Last Update: 
	Description: 
	Source: 
	Units: 
	Remarks: 
	History:
'''


class coef(pytrix.vector):
	def __init__(self,coefs):
		self.data = list(coefs)  #name matters: see superclass methods
		self.coefSE = None
		self.length = len(self.data)
		#result_class is for overriding result class in subclasses
		self.result_class = pytrix.vector
		#core_attr: attributes to check conformability (see require_samecore)
		self.core_attr = dict(length=self.length)

class Series(pytrix.vplus):
	'''Basic class for fixed frequency time series.
	(Subclasses pytrix.vplus which subclasses pytrix.vector.)

	:todo: rethink full and current smpl
	'''
	def __init__(self,data,smpl=None,**kwds):
		logging.debug("\n\tEntering class series.")
		self.result_class = series  #override vplus
		self.data = list(data)
		self.nobs = len(data)
		if 'length' in kwds:
			assert(self.nobs==kwds['length']),"Data length does not match provided length"
		if 'smpl' is None:
			self.smpl_full = (1,self.nobs)
		elif isinstance(smpl,tuple):
			assert(self.nobs==1+self.smpl_full[1]-self.smpl_full[0]), "Number of obs does not match sample."
			self.smpl_full = smpl
		elif isinstance(smpl,io.Sample):
			assert len(data)==len(smpl.get_dates()), "Number of obs does not match sample."
			self.smpl_full = smpl.copy()
		else:
			raise TypeError('class series: Unrecognized smpl type.')
		#self.label = label             #TODO: add label object?
		self.dstat = None
		self.core_attr = dict(length=self.nobs,smpl=self.smpl_full)  #TODO: is this the best core?
		print "####################################"
	def __repr__(self):
		return "series:\n"+str(self.data)
	def __getitem__(self, item):  #http://www.python.org/doc/2.3.4/whatsnew/section-slices.html
		return self.data.__getitem__(item)
		'''
		if isinstance(item, slice):
			indices = item.indices(len(self.data))  #TODO: shd this interact w sample??
			return [self.calc_item(i) for i in range(*indices)]  #TODO:return list or series (w appropriate sample)??
		else:
			return self.calc_item(item)
		'''
	def stat(self):
		# for comparable functionality see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/409413
		if not self.dstat:
			self.dstat = dstat(self.data)
		keys = [
		Mean,
		Median,
		StdDev,
		Skewness,
		Kurtosis,
		Jarque-Bera,
		JBProbability,
		Sum,
		SumSqDev,
		Observations,
		Maximum,
		Minimum,
		]
	#TODO: shd we use __call__ for shifting?
	#see: http://docs.python.org/ref/callable-types.html
	def shift(self,offset):
		'''Return lead or lag of series: x.shift(n) = F^n x
		'''
		assert(isinstance(offset,int))
		if offset < 0: #lag series
			new_data = self.data[0:offset]
			new_dates = self.smpl_full.get_dates()[-offset:]
		if offset > 0: #lead series
			new_data = self.data[offset:]
			new_dates = self.smpl_full.get_dates()[:-offset]
		if offset == 0:
			return self.copy()
		else:
			return series(new_data,io.Sample(new_dates[0],new_dates[-1],freq=self.smpl_full.freq,dates=new_dates))
	def d(self,n=1,s=0):
		'''Return (1-L)^n(1-L^s)x.'''
		assert(s==int(s) and n==int(n)), "Fractional differences not supported."
		assert(s >= 0 and n >=0), "Postive differences required"	#TODO
		dnsx = self[:]
		if s>0:
			dnsx = [dnsx[i]-dnsx[i-s] for i in range(s,len(dnsx))]
		if n>0:
			for idx in range(n):
				dnsx = [dnsx[xi]-dnsx[xi-1] for xi in range(1,len(dnsx))]
		logging.info('series.d(): Full sample of series: '+str(self.smpl_full))
		if isinstance(self.smpl_full,tuple):
			dsmpl = (self.smpl_full[0]+n+s,self.smpl_full[1]) 
			logging.debug('series.d(): Modified tuple: '+str(dsmpl))
		else:
			old_dates = self.smpl_full.get_dates()
			dsmpl = io.Sample(old_dates[n+s],
							  old_dates[-1],
							  freq=self.smpl_full.freq)
			logging.debug('series.d(): Modified sample: '+str(dsmpl))
		logging.debug("series.d(): n=%i,s=%i,dsmpl=%s"%(n,s,dsmpl))
		return series(dnsx,smpl=dsmpl)
	def transform(self,fn):
		if isinstance(self.smpl_full,io.Sample):
			smpl_copy=self.smpl_full.copy()
		else:
			smpl_copy=self.smpl_full
		return series([fn(xi) for xi in self],smpl=smpl_copy)
	def detrend_linear(self,zeroperiod=0): #TODO allow normalization to different date
		#wd it be worth doing it directly, e.g. TODO
		if have_scipy:
			x11 = self.nobs
			x12 = x11*(x11-1)/2
			x22 = (scipy.arange(x11)*scipy.asarray(self.data)).sum()
			xTx = scipy.mat([[x11,x12],[x12,x22]])
		intercept = itertools.cycle([1])
		trend = xrange(self.nobs)
		X = zip(intercept,trend)
		return pytrix.Ols(self.data,X).get_resids()
	def plot(self, plottype='line', smpl=None):
		if not smpl:
			dates = self.smpl_full.get_dates()
			data = self.data
		else:
			# specified sample may be outside data range: compensate
			#TODO: fix for undated data
			smpl_sub = io.Sample(max(smpl.start,self.smpl_full.start),
			                  min(smpl.end,self.smpl_full.end),
			                  self.smpl_full.freq)
			dates = smpl_sub.get_dates()
			# make list of dates for full sample (from its rrule)
			temp = self.smpl_full.get_dates()
			# get the index for the start & end dates of the subsample
			idx_start = temp.index(dates[0])
			idx_end = temp.index(dates[-1])
			# get the data corresponding to the subsample
			data = self.data[idx_start:idx_end+1]
		fig = matplotlib.figure.Figure(figsize=(5,4))
		ax = fig.add_subplot(111)
		if plottype == 'line':
			logging.info("Make line plot.")
			ax.plot_date(date2num(list(dates)), data, '-', color=(1,0,0))
			ax.set_xlabel('Time')
			show_tkagg(fig)
		#pylab.plot(range(len(self.data)),self.data,'r-')
		#pylab.show()
	def get_data(self,smpl=None,freq=None):
		'''Return series data, possibly subsampled.

		:todo: frequency conversion  NEEDS MUCH WORK!!!
		'''
		data = self.data
		if freq:
			oldfreq = self.smpl_full.freq 
			newfreq = io.freq2num(freq)
			if newfreq == oldfreq:
				pass
			elif newfreq ==1 and oldfreq == 4:
				return [data[i] for i in range(0,len(data),4) ]
			elif newfreq == 1 and oldfreq == 12:
				return [data[i] for i in range(0,len(data),12) ]
			else:
				raise NotImplementedError('frequency conversion not yet implemented')
		if smpl is not None:
			if isinstance(smpl,tuple):
				firstind = smpl[0]
				lastind = smpl[1]
			elif isinstance(smpl,io.Sample):
				firstind = self.smpl_full.get_date_index(smpl.start)
				lastind = self.smpl_full.get_date_index(smpl.end)
			else:
				raise ValueError('smpl must be tuple or sample instance')
			return self.data[firstind:lastind+1]
		else:
			return self.data
	def get_subsample(self,smpl=None,freq=None):
		'''Return list of series data, possibly subsampled.

		:note: currently get_data already returns a list; see get_item in vector class
		'''
		assert(isinstance(self.smpl_full,io.Sample) and isinstance(smpl,io.Sample))
		assert (smpl.start >= self.smpl_full.start)and(smpl.end <= self.smpl_full.end)
		return series(self.get_data(smpl,freq),smpl)

class series(Series):
	#old name; deprecated
	pass


def show_tkagg(figure,title=''):
	"""Create a new matplotlib figure manager instance.
	"""
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	#_focus = windowing.FocusManager()
	window = Tk.Tk()
	window.wm_title(title)
	canvas = FigureCanvasTkAgg(figure, master=window)    
	canvas.draw()
	canvas.get_tk_widget().pack()
	Tk.mainloop()




class DstatSimple(object):
	'''Simple descriptive statistics: no missing value handling!

	References::

		http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/409413
		http://www.jennessent.com/arcview/sum_stats.htm
		http://en.wikipedia.org/wiki/Skewness
		http://en.wikipedia.org/wiki/Kurtosis

	Available instance attributes::

       nobs: total number of elements in the data set
       sum:  sum of all values (n) in the data set
       min:  smallest value of the data set
       max:  largest value of the data set
       mode: value(s) that appear(s) most often in the data set
       mean: arithmetic average of the data set
       zscores: vector of z-scores
       #range:  difference between the largest and smallest value in the data set
       median:  value which is in the exact middle of the data set
       m2: measure of the spread of the data set about the mean: MLE
       var: measure of the spread of the data set about the mean: unbiased
       std: standard deviation - measure of the dispersion of the data set based on var
       skew: sample skewness
       kurtosis: sample kurtosis
       jb: Jarque-Bera statistic
       jbpval: Jarque-Bera statistic's pvalue (Chi^2 df=2)

	:todo: direct support for series objects
	:todo: add missing value handling? (but SciPy has this)
	:note: Don't plan to add: Sum Sq. Dev.
	'''
	def __init__(self, v, name=None, smpl=None, mv=None):
		if not v: raise ValueError('empty sample')
		self.data = v #no copy!
		self.id = id(self) #instance id
		self.name = name
		self.smpl = smpl
		#from scipy.stats.stats import mean, variation, skew, kurtosis, histogram
		self.__nobs = None
		self.__sum = None
		self.mean = self.sum/self.nobs
		self.m2, self.m3, self.m4 = self.__get_cmoments(v)
		# m2 is MLE variance estimate (biased)
		# var is standard def of sample variance, not MLE estimate
		try: self.var =  self.m2*self.nobs/(self.nobs-1)
		except ZeroDivisionError: self.var = 0
		self.std =  math.sqrt(self.var) #based on sample variance
		self.__zscores = None   #delay calc until needed
		self.__mode = None
		self.median = self.__get_median(v)
		self.skew = self.m3/math.sqrt(self.m2)**3
		self.kurtosis = self.m4/self.m2**2			#NOT kurtosis excess (=kurtosis-3)
		#Jarque-Bera: JB(X)=\frac{T}{6}\left[S^{2}(X) + \frac{[K(X)-3]^{2}}{4}\right]
		self.jb = (self.skew**2 + (self.kurtosis-3)**2/4)*self.nobs/6
		if have_scipy:
			self.jbpval = scipy.stats.stats.chisqprob(self.jb,2) #check TODO
		else:
			self.jbpval = None
		self.min = min(v)
		self.max = max(v)
		pylab.figure()
		pylab.hist(v)
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
		('Median',self.median),
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
	def __get_nobs(self):
		if self.__nobs is None:
			self.__nobs = len(self.data)
		return self.__nobs
	nobs = property(__get_nobs,None,None,"Number of observations (length of series).")
	def __get_sum(self):
		if self.__sum is None:
			self.__sum = float(sum(self.data))
		return self.__sum
	sum = property(__get_sum,None,None,"sum of series values")
	def __get_zscores(self):
		if self.__zscores is None:
			self.__zscores = [(vi - self.mean)/self.std for vi in self.data]
		return self.__zscores
	zscores = property(__get_zscores,None,None,"z-scores for this series")
	def __get_cmoments(self,v,m=[2,3,4]):
		cmoments=[]
		for xp in m:
			cmoments.append(sum([(x-self.mean)**xp for x in v])/self.nobs) 
		return tuple(cmoments)
	def __get_median(self,v):
		vs = v[:]
		vs.sort()
		median = not self.nobs%2 \
		        and (vs[self.nobs//2-1]+vs[self.nobs//2])/2.0 \
		        or  vs[self.nobs//2] #if even, return midpt
		return median
	def __get_mode(self):
		# but see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/277600
		# for more efficient method using dictionary
		if self.__mode is None:
			v = self.data
			mode = []
			try: counts = [(v.count(x),x) for x in set(v)]
			except NameError:
				from sets import Set as set  #needed for Python 2.3
				counts = [(v.count(x),x) for x in set(v)]
			maxct = max(counts)[0]
			if maxct > 1:
				mode = [x[1] for x in counts if x[0]==maxct]
			self.__mode = mode
		return self.__mode
	mode = property(__get_mode,None,None,"modal value of series")
	def test(self):
		logging.info( "Testing computations:" )
		if have_numpy:
			x = N.array(self.data)
			assert(self.nobs == x.size)
			assert(self.sum == x.sum())
			assert(self.min == x.min())
			assert(self.max == x.max())
			assert(self.mean == x.mean())
			assert(self.m2 == N.var(x))
			assert(self.std == N.std(x))
		if have_scipy:
			assert(self.zscores == scipy.stats.zs(x))
			assert(self.median == scipy.stats.median(x))
			'''
			#mode: value(s) that appear(s) most often in the data set
		  #range: difference between the largest and smallest value in the data set
			 m2: measure of the spread of the data set about the mean: MLE
		   var: measure of the spread of the data set about the mean: unbiased
		   std: standard deviation - measure of the dispersion of the data set based on var
		   skew: sample skewness
	   kurtosis: sample kurtosis
			 jb: Jarque-Bera statistic
		 jbpval: Jarque-Bera statistic's pvalue (Chi^2 df=2)
			'''
		
def varlags(var,lags):
	'''Prepare data for VAR. ::
	
	         x,xlags  = varlags(var,lags)

	OUTPUT::
	
	        x -     (T - lags) x K array, the last T-lags rows of var
	        xlags - (T - lags) x lags*cols(var) array,
	                being the 1st through lags-th
	                values of var corresponding to the values in x
	                i.e, the appropriate rows of x(-1)~x(-2)~etc.

	:param `var`:  - T x K array or list
	:param `lags`: - scalar, number of lags of var (a positive integer)
	:author: Alan G. Isaac
	:since: 5 Aug 2004
	:note: get current version from pyGAUSS
	'''
	xlags=var[lags-1:-1]
	for i in range(2,lags+1):
		xlags=N.concatenate([xlags,var[lags-i:-i]],1)
	return N.array(var[lags:],copy=1),xlags


if __name__ == "__main__":
	'''Example use for module.
	'''
	cpi = series(*io.fetch(r'h:\data\FRED\cpi\CPIAUCNS.db'))
	sub = io.Sample([1950,1],[1990,1],12)
	print sub
	cpi.plot()
	cpi.plot(smpl=sub)
	#print DstatSimple([1,1,2,2,3,3,3]Last modified: 2006 Jun 30
	#print DstatSimple(cpi.get_data(),'cpi',cpi.smpl_full)
	#pylab.show()

