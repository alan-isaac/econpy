"""Simple time series manipulations.

:note: Run as __main__ to see example use.
:author: Alan G. Isaac, except where otherwise specified.
:since: 2004-08-04
:date: 2007-08-23
:copyright: 2005 Alan G. Isaac, except where otherwise specified.
:license: `MIT license`_
:see: pytrix.py
:see: io.py
:see: stat.py
:see: pyGAUSS.py

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import division, absolute_import
__docformat__ = "restructuredtext en"

#standard library imports
import logging
logging.getLogger().setLevel(logging.WARN) #sets root logger level
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

#package imports
from .pytrix import Vector, Vplus   #`Series` subclasses `Vector`
from .io import freq2num, Sample, fetch, write_db
from .stat import Dstat1

try:
	import numpy as np
	from numpy import linalg
except ImportError:
	logging.error("numpy required for this module")
	raise
have_scipy = False
try:
	import scipy
	have_scipy = True
except ImportError:
	logging.info("SciPy not available")
try:
	import statsmodels.api as sm
	have_sm = True
except ImportError:
	logging.info("statsmodels not available")



"""
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
"""


class coef(Vector):
	def __init__(self,coefs):
		self.data = list(coefs)  #name matters: see superclass methods
		self.coefSE = None
		self.length = len(self.data)
		#result_class is for overriding result class in subclasses
		self.result_class = vector
		#core_attr: attributes to check conformability (see require_samecore)
		self.core_attr = dict(length=self.length)

class Series(Vplus):
	"""Basic class for fixed frequency time series.
	(Subclasses pytrix.vplus which subclasses pytrix.vector.)

	:todo: rethink full and current smpl
	"""
	def __init__(self, data, smpl=None, comments=None, **kwds):
		logging.debug("\n\tEntering Series.__init__.")
		self.result_class = Series  #override vplus
		self.data = list(data)
		self.nobs = len(data)
		self.comments = comments or dict()
		if 'length' in kwds:
			assert(self.nobs==kwds['length']),"Data length does not match provided length"
		if smpl is None:
			self.smpl_full = (1,self.nobs)
		elif isinstance(smpl,tuple):
			assert(self.nobs==1+self.smpl_full[1]-self.smpl_full[0]), "Number of obs does not match sample."
			self.smpl_full = smpl
		elif isinstance(smpl, Sample):
			assert len(data)==len(smpl.dates), "Number of obs does not match sample."
			self.smpl_full = smpl.copy()
		else:
			raise TypeError('class Series: %s is an unrecognized smpl type.'%smpl)
		#self.label = label             #TODO: add label object?
		self.dstat = None
		self.core_attr = dict(length=self.nobs,smpl=self.smpl_full)  #TODO: is this the best core?
		logging.info('leave Series.__init__')
	def __repr__(self):
		return "series:\n"+str(self.data)
	def __getitem__(self, item):  #http://www.python.org/doc/2.3.4/whatsnew/section-slices.html
		return self.data.__getitem__(item)
		"""
		if isinstance(item, slice):
			indices = item.indices(len(self.data))  #TODO: shd this interact w sample??
			return [self.calc_item(i) for i in range(*indices)]  #TODO:return list or series (w appropriate sample)??
		else:
			return self.calc_item(item)
		"""
	def stat(self):
		# for comparable functionality see http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/409413
		if not self.dstat:
			self.dstat = Dstat1(self.data)
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
	def shift(self, offset):
		"""Return lead or lag of series: x.shift(n) = F^n x
		"""
		assert(isinstance(offset,int))
		if offset < 0: #lag series
			new_data = self.data[0:offset]
			new_dates = self.smpl_full.dates[-offset:]
		if offset > 0: #lead series
			new_data = self.data[offset:]
			new_dates = self.smpl_full.dates[:-offset]
		if offset == 0:
			return self.copy()
		else:
			return series(new_data,Sample(new_dates[0],new_dates[-1],freq=self.smpl_full.freq,dates=new_dates))
	def d(self, n=1, s=0):
		"""Return (1-L)^n(1-L^s)x."""
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
			old_dates = self.smpl_full.dates
			dsmpl = Sample(old_dates[n+s],
							  old_dates[-1],
							  freq=self.smpl_full.freq)
			logging.debug('series.d(): Modified sample: '+str(dsmpl))
		logging.debug("series.d(): n=%i,s=%i,dsmpl=%s"%(n,s,dsmpl))
		return series(dnsx,smpl=dsmpl)
	def transform(self, fn):
		if isinstance(self.smpl_full,Sample):
			smpl_copy=self.smpl_full.copy()
		else:
			smpl_copy=self.smpl_full
		return series([fn(xi) for xi in self],smpl=smpl_copy)
	def detrend_linear(self, zeroperiod=0): #TODO allow normalization to different date
		#wd it be worth doing it directly, e.g. TODO
		if have_scipy:
			x11 = self.nobs
			x12 = x11*(x11-1)/2
			x22 = (scipy.arange(x11)*scipy.asarray(self.data)).sum()
			xTx = scipy.mat([[x11,x12],[x12,x22]])
		intercept = itertools.cycle([1])
		trend = xrange(self.nobs)
		X = zip(intercept,trend)
		return OLS(self.data,X).resids   #from ls.py
	def tolist(self, copy=True):
		"""Return series data, possibly subsampled.

		"""
		logging.debug("Enter Series.tolist.")
		if copy:
			data = list(self.data)
		else:
			data = self.data
		return data
	def write2databank(self, file_name):
		write_db(file_name=file_name, data=self.tolist(), smpl=self.smpl_full, comments=self.comments)
	def subsample(self, smpl=None, freq=None):
		"""Return list of series data, possibly subsampled.

		:note: freq overrides smpl.freq
		:note: currently tolist already returns a list; see get_item in vector class
		:todo: frequency conversion  NEEDS MUCH WORK!!!
		"""
		logging.info("Enter Series.subsample.")
		data = self.tolist(copy=True)
		full = self.smpl_full
		if smpl is not None:
			assert (isinstance(self.smpl_full,Sample) and isinstance(smpl,Sample))
			assert (smpl.start >= self.smpl_full.start)and(smpl.end <= self.smpl_full.end)
			logging.debug("\n\tSubsample based on smpl.")
			#we do NOT (!) change frequency at this point
			if isinstance(smpl, tuple):
				logging.warn('using tuple')
				idx_start = smpl[0]
				idx_end = smpl[1]
			elif isinstance(smpl, Sample):
				logging.warn('using Sample')
				idx_start = full.get_date_index(smpl.start)
				idx_end = full.get_date_index(smpl.end)
			else:
				raise ValueError('smpl must be tuple or sample instance')
			data = data[idx_start:idx_end+1]
		else:
			logging.info('smpl is None')
		newfreq = freq2num(freq or smpl.freq)
		if smpl and (smpl.freq != newfreq):
			msg = """Frequency of %s
			does not match smpl frequency of %s"%(newfreq,smpl.freq)).
			Adjusting smpl frequency."""
			logging.warn(msg)
			smpl = Sample(smpl.start, smpl.end, freq=newfreq)
		oldfreq = full.freq 
		if newfreq != oldfreq:
			old2new = {
				(4,1) : slice(0, len(data), 4),
				(12,1) : slice(0, len(data), 12),
				}
			logging.debug("Frequency conversion required.")
			try:
				myslice = old2new[(oldfreq, newfreq)]
			except KeyError:
				raise NotImplementedError('Unsupported frequency conversion.')
			data = data[myslice]
		else:
			myslice = slice(0, len(data), 1)
		if smpl is None:  #construct a sample for dated series
			if isinstance(self.smpl_full,Sample):
				dates = self.smpl_full.dates[myslice]
				start, end = dates[0], dates[-1]
				smpl = Sample(start=start, end=end, freq=freq, dates=dates)
		return Series(data=data, smpl=smpl, comments=self.comments)
	def plot(self, plottype='line', smpl=None):
		if not smpl:
			dates = self.smpl_full.dates
			data = self.data
		else:
			# specified sample may be outside data range: compensate
			#TODO: fix for undated data
			smpl_sub = Sample(max(smpl.start,self.smpl_full.start),
			                  min(smpl.end,self.smpl_full.end),
			                  self.smpl_full.freq)
			dates = smpl_sub.dates
			# make list of dates for full sample (from its rrule)
			temp = self.smpl_full.dates
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

class series(Series):
	def __init__(self):
		Series.__init__(self)
		logging.warn("\n\tWe have deprecated `series`; please use `Series`.")

def show_tkagg(figure, title=''):
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




		
def varlags(xtk, lags):
	"""Return tuple, the data prepared for a VAR.
	
	Usage::
	
	         x,xlags  = varlags(xtk, lags)

	OUTPUT::
	
	        x -     (T - lags) x K array, the last T-lags rows of xtk
	        xlags - (T - lags) x lags*K array,
	                being the 1st through lags-th
	                values of xtk corresponding to the values in x
	                i.e, the appropriate rows of x(-1)~x(-2)~etc.

	Parameters
	----------
	`xtk` :  array or list (2d: T x K)
	   the K VAR variables in K columns, row 0 being most recent observeration
	`lags` : int
	   number of lags of xtk (a positive integer)

	:author: Alan G. Isaac
	:since: 5 Aug 2004
	:date: 2010-06-01
	:note: get current version from pyGAUSS.py
	"""
	xtk = np.asarray(xtk)
	try:
		T, K = xtk.shape
	except ValueError:
		raise ValueError('Input array must be 2d')
	xlagslst = [ xtk[lags-i:-i] for i in range(1,lags+1)]
	xlags = np.hstack( xlagslst )
	assert ((T-lags,K) == xtk[lags:].shape)
	assert ((T-lags,lags*K) == xlags.shape)
	return xtk[lags:].copy(), xlags


def hpfilter(x, penalty=1600):
	"""Return tuple, (cycle, trend).

	Parameters
	----------
	x : array-like
		The 1d timeseries to filter.
	penalty : float
		The Hodrick-Prescott smoothing parameter. A value of 1600 is
		suggested for quarterly data. Ravn and Uhlig suggest using a value
		of 6.25 (1600/4**4) for annual data and 129600 (1600*3**4) for monthly
		data.

	Assumes x is 1d; penalty is often called 'lambda'.
	"""
	if have_sm:
		return sm.tsa.filters.hpfilter(x, penalty)
	else:
		return hpfilter03(x, penalty)


'''
def hpfilter01(y, penalty=1600):
	"""Return: (t,d) trend and deviation
	Based on Lubuele's GAUSS code:
	http://www.american.edu/academic.depts/cas/econ/gaussres/timeseri/hodrick.src
	which is a translation of Prescott's fortran code:
	http://dge.repec.org/codes/prescott/hpfilter.for (Prescott's code)
	which is a 2-pass Kalman filter.
	assumes y is 1d
	penalty is often called 'lambda'
	"""
	s = penalty
	assert (s>0)
	n = len(y)
	assert (n>3)
	t = [0]*n  #1d
	d = [0]*n  #1d
	v = np.zeros( (n,3) )
	m1 = y[1]   #changed to zero-based indexing
	m2 = y[0]   #changed to zero-based indexing
	i1 = 3
	i2 = n

	#initialize v
	v11 = 1
	v22 = 1
	v12 = 0
	i = i1    #i initially 3, increments each pass
	istep = 1
	while (i <= i2): #first pass
		#subroutine_pass()
		x = m1
		m1 *= 2
		m1 -= m2
		m2 = x
		x = v11
		z = v12
		v11 = 1/s+4*(x-z)+v22
		v12 = 2*x-z
		v22 = x
		dett = v11*v22-v12*v12
		if istep == 1:  #counting fwd
			v[i-2,0] = v22/dett #changed to zero-based indexing
			v[i-2,2] = v11/dett #changed to zero-based indexing
			v[i-2,1] = -v12/dett #changed to zero-based indexing
			t[i-2] = v[i-2,0]*m1+v[i-2,1]*m2 #changed to zero-based indexing
			d[i-2] = v[i-2,1]*m1+v[i-2,2]*m2 #changed to zero-based indexing
		elif i >= 2: #counting backward
			b11 = v11/dett
			b12 = -v12/dett
			b22 = v22/dett
			e1 = b11*m2+b12*m1+t[i-1] #changed to zero-based indexing
			e2 = b12*m2+b22*m1+d[i-1] #changed to zero-based indexing
			b12 += v[i-1,1] #changed to zero-based indexing
			b22 += v[i-1,2] #changed to zero-based indexing
			b11 += v[i-1,0] #changed to zero-based indexing
			dett = b11*b22-b12*b12
			t[i-1] = (-b12*e1+b11*e2)/dett
		x = v11+1
		z = (y[i-1]-m1)/x #changed to zero-based indexing
		m1 += v11*z
		m2 += v12*z
		z = v11
		v11 -= v11*v11/x
		v22 -= v12*v12/x
		v12 -= z*v12/x
		i += istep
	t[-1] = m1  #ok
	t[-2] = m2  #ok
	m1 = y[-2]  #ok
	m2 = y[-1]  #ok
	i1 = n-2
	i2 = 1
	v11 = 1
	v22 = 1
	v12 = 0
	i = i1
	istep = -1
	while (i >= i2): #second backward pass
		#subroutine_pass()
		x = m1
		m1 *= 2
		m1 -= m2
		m2 = x
		x = v11
		z = v12
		v11 = 1/s+4*(x-z)+v22
		v12 = 2*x-z
		v22 = x
		dett = v11*v22-v12*v12
		if istep == 1:  #counting fwd
			v[i-2,0] = v22/dett #changed to zero-based indexing
			v[i-2,2] = v11/dett #changed to zero-based indexing
			v[i-2,1] = -v12/dett #changed to zero-based indexing
			t[i-2] = v[i-2,0]*m1+v[i-2,1]*m2 #changed to zero-based indexing
			d[i-2] = v[i-2,1]*m1+v[i-2,2]*m2 #changed to zero-based indexing
		elif i >= 2: #counting backward
			b11 = v11/dett
			b12 = -v12/dett
			b22 = v22/dett
			e1 = b11*m2+b12*m1+t[i-1] #changed to zero-based indexing
			e2 = b12*m2+b22*m1+d[i-1] #changed to zero-based indexing
			b12 += v[i-1,1] #changed to zero-based indexing
			b22 += v[i-1,2] #changed to zero-based indexing
			b11 += v[i-1,0] #changed to zero-based indexing
			dett = b11*b22-b12*b12
			t[i-1] = (-b12*e1+b11*e2)/dett
		x = v11+1
		z = (y[i-1]-m1)/x #changed to zero-based indexing
		m1 += v11*z
		m2 += v12*z
		z = v11
		v11 -= v11*v11/x
		v22 -= v12*v12/x
		v12 -= z*v12/x
		i += istep
	t[0] = m1   #changed to zero-based indexing
	t[1] = m2   #changed to zero-based indexing
	i = 0   #changed to zero-based indexing
	while i < n:   #changed to zero-based indexing
		d[i] = y[i]-t[i]
		i = i+1
	return (t,d)
'''


def hpfilter02(x, penalty=1600):
	"""Return: (cycle, trend), based on Heer and Maussner.
	Requires ``scipy`` (for sparse matrices).

	Parameters
	----------
	x : array-like
		The 1d timeseries to filter.
	penalty : float
		The Hodrick-Prescott smoothing parameter. A value of 1600 is
		suggested for quarterly data. Ravn and Uhlig suggest using a value
		of 6.25 (1600/4**4) for annual data and 129600 (1600*3**4) for monthly
		data.

	Assumes x is 1d; penalty is often called 'lambda'.

	Conceptualize the calculation as follows:
	eye <- diag( length(y) )
	d2 <- diff( eye, d=2 )
	z <- solve( eye + penalty * crossprod(d2),  y )
	"""
	#local m, i, nobs;
	import numpy as np
	from scipy.linalg import solveh_banded

	nobs = len(x)
	m = np.zeros((3, nobs))
	#construct the banded matrix
	for i in range(nobs):
		m[0,i] = penalty;
		m[1,i] = -4*penalty;
		m[2,i] = 1 + 6*penalty;
	m[0,0] = 0
	m[1,0] = 0
	m[2,0] = 1+penalty

	m[0,1] = 0
	m[1,1] = -2*penalty
	m[2,1] = 1+5*penalty

	m[1,nobs-1] = m[1,1]
	m[2,nobs-1] = m[2,0]
	m[2,nobs-2] = m[2,1]

	trend = solveh_banded(m, x)
	cycle = x - trend
	return cycle, trend

def diagrv(x, v, k=0, copy=True):
	"""Return 2d array, the array `x` with the vector `v`
	substituted for its k-th diagonal. For 2d arrays only.
	For k=0 and copy=False, equivalent to::

		idx = list( range( min(nrows,ncols) ) )
		x[idx, idx] = v
	"""
	x = np.array(x, copy=copy )
	try:
		nrows, ncols = x.shape
	except ValueError:
		raise ValueError("diagrv is defined for 2-d arrays only.")
	stride = 1 + ncols
	m = min(nrows, ncols)
	if (k >= 0):
		assert (k < ncols)
		nvals = min(ncols-k, nrows)
	else:
		assert (k < nrows)
		nvals = min(nrows+k, ncols)
		k *= -ncols
	#flat works even if `x` not continguous!
	x.flat[ slice(k,k+nvals*stride,stride) ] = v
	return x

def hpfilter03(x, penalty):
	"""Return: (cycle, trend), as determined by
	a standard Hodrick-Prescott filter.
	Requires numpy.  Does not use scipy,
	so does not use sparse or compacted matrices.
	The trend is the smoothed (filtered) series.
	The cycle is (x - trend).

	Conceptualize the calculation in R notation as follows:
	https://stat.ethz.ch/pipermail/r-help/2002-March/019283.html
	eye <- diag( length(y) )
	d2 <- diff( eye, d=2 )
	z <- solve( eye + penalty * crossprod(d2),  y )

	Parameters
	----------
	x : array-like
		The 1d timeseries to filter.
	penalty : float
		The Hodrick-Prescott smoothing parameter. A value of 1600 is
		suggested for quarterly data. Ravn and Uhlig suggest using a value
		of 6.25 (1600/4**4) for annual data and 129600 (1600*3**4) for monthly
		data.
	"""
	T = len(x)
	a = 6*penalty+1
	b = -4*penalty
	c = penalty
	mtest = np.zeros((T,T), dtype=x.dtype)
	diagrv(mtest,a,k=0,copy=False)
	diagrv(mtest,b,k=1,copy=False)
	diagrv(mtest,b,k=-1,copy=False)
	diagrv(mtest,c,k=2,copy=False)
	diagrv(mtest,c,k=-2,copy=False)
	#change first block
	mtest[:2,:2] = [[1+penalty,-2*penalty],[-2*penalty,1+5*penalty]]
	#change last block
	mtest[-2:,-2:] = [[1+5*penalty,-2*penalty],[-2*penalty,1+penalty]]
	trend = linalg.solve(mtest,x)
	return x-trend, trend




if __name__ == "__main__":
	#test the results against statsmodels
	if have_sm:
		dta = sm.datasets.macrodata.load()
		X = dta.data['realgdp']
		cycle0, trend0 = sm.tsa.filters.hpfilter(X,1600)
		cycle3, trend3 = hpfilter03(X, 1600)
		assert np.allclose(cycle0, cycle3)
		cycle2, trend2 = hpfilter02(X, 1600)
		assert np.allclose(cycle0, cycle2)
		#cycle1, trend1 = hpfilter01(X, 1600)
		#assert np.allclose(cycle0, cycle1)
	"""
	#example use
	cpi = series(*fetch(r'h:\data\FRED\cpi\CPIAUCNS.db'))
	sub = Sample([1950,1],[1990,1],12)
	print sub
	cpi.plot()
	cpi.plot(smpl=sub)
	#print Dstat1([1,1,2,2,3,3,3]Last modified: 2006 Jun 30
	#print Dstat1(cpi.tolist(),'cpi',cpi.smpl_full)
	#pylab.show()
	"""

