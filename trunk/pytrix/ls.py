"""Various least squares routines.
Some are lightweight, in the sense that they do not depend on an array package.

:needs: Python 2.5.1+
:see: `pytrix.py <http://www.american.edu/econ/pytrix/pytrix.py>`
:see: `pyGAUSS.py <http://www.american.edu/econ/pytrix/pyGAUSS.py>`
:see: tseries.py
:see: unitroot.py
:see: pytrix.py
:see: io.py
:todo: conform to http://svn.scipy.org/svn/scipy/trunk/scipy/stats/models/
:note: Please include proper attribution should this code be used in a research project or in other code.
:see: The code below by William Park and more can be found in his `Simple Recipes in Python`_
:copyright: 2007 Alan G. Isaac, except where another author is specified.
:license: `MIT license`_ except where otherwise specified.
:since: 2004-08-04

.. _`Simple Recipes in Python`: http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import division, absolute_import
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '2007-09-10'

from .utilities import have_numpy, have_scipy
if have_numpy:
	import numpy as np
	import numpy.linalg as la
if have_scipy:
	from scipy import stats as Sstats

import random, math, operator
import types
import sys,os
import logging
logging.basicConfig(level=logging.WARN)
import time




class OLS(object):
	"""Provides least squares estimates for a **single** equation,
	where `dep` is Tx1 and `indep` is TxK.  (Both are 2d!)
	Each row of `dep` and `indep` is an observation; for time series,
	row 0 should contain the oldest observation.

	Example use::

		result = OLS(dep, indep)
		print result
		print result.resids
	
	:Ivariables:
		`nobs` : int
			rows(dep), the number of observations
		`coefs` : float array
			the least squares solution
		`cov` : array
			2d covariance array for coefficient estimates
		`se` : array
			coefficient standard errors
		`tvals` : array
			t-ratios for the coefficient estimates
		`pvals` : array
			p-values for the coefficient estimates
		`fitted` : array
			Tx1 array (indep * coefs)
		`resids` : array
			Tx1 array (dep - indep * coefs)
		`sigma2` : float
			(resids' * resids)/(T-K)
		`pvalF` : scalar
			p-value for regression F statistic, based on F distribution
		`xTx` : array
			KxK array (roughly, indep' * indep)
		`xTy` : array
			Kx1 array (indep' * dep)
	:warning: adds intercept
	:requires: NumPy
	:see: Russell Davidson and James G. MacKinnon,
          _Estimation and Inference in Econometrics_
          (New York: Oxford, 1993)
	:see: http://www.scipy.org/Cookbook/OLS different approach but shared goals
	:todo: accept recarrays
	:date: 2006-12-08
	:since: 2004-08-11
	:author: Alan G. Isaac
	"""
	def __init__(self, dep, indep=None, dep_name='', indep_names=(), constant=1, trend=None):
		"""
		:Parameters:
			`dep` : array
				(T x 1) array, the LHS variable
			`indep` : array
				(T x K) array, the RHS variables, in columns
		"""
		assert isinstance(dep_name,str), "Names must be strings."
		if not have_numpy:
			raise NotImplementedError('NumPy required for OLS.')
		Y = np.asarray(dep).reshape(-1,1)  #TODO single equation only
		self.Y = Y
		self.nobs = len(Y)
		#make X sets self.nvars, self.nobs, self.indep_names
		self.indep_names = list(indep_names)
		X = np.asarray( self.makeX(indep=indep, constant=constant, trend=trend) )
		self.X = X  #used for end_points ... need for anything else?
		coefs, ess = np.linalg.lstsq(X,Y)[:2]  #OLS estimates and ess
		self.ess = ess  #sum of squared residuals
		assert (len(dep) == len(X)), "Number of observations do not agree."
		self.dep_name = dep_name or 'y'
		#data based attributes
		self.xTx = np.dot(X.T , X)
		self.xTy = np.dot(X.T , Y)
		self.fitted = np.dot(X,coefs)
		resids = np.ravel(Y - self.fitted)
		assert abs(self.ess - np.dot(resids,resids))<0.001 #check error sum of squares TODO: delete
		self._resids = resids                          #resids is a property
		#end of matrix algebra
		self.coefs = np.ravel(coefs)                     #self.coefs is a 1d array
		self.df_e = self.nobs - self.ncoefs				# degrees of freedom, error 
		self.sigma2 = self.ess / self.df_e              # sigma^2 = e'e/(T-K)
		self.llf, self.aic, self.bic = self.llf()
		# convenience declarations: attributes to be computed as needed
		self._cov = None                                #the parameter covariance matrix
		self._standard_errors = None                    #the parameter standard errors
		self._tvals = None
		self._pvals = None
		self._rols_coefs = None                         #one row per observation
		# other attributes
		t = time.localtime()
		self.date = time.strftime("%a, %d %b %Y",t)
		self.time = time.strftime("%H:%M:%S",t)
		################
		#stuff from Vince
		################ 
		self.yvar = Y.var()
		self.R2 = 1 - self.resids.var()/self.yvar			# model R-squared
		self.R2adj = 1-(1-self.R2)*((self.nobs-1)/(self.nobs-self.ncoefs))	# adjusted R-square 
		self.df_r = self.ncoefs - 1						# degrees of freedom, regression 
		self.F = (self.R2/self.df_r) / ((1-self.R2)/self.df_e)	# model F-statistic
		self._pvalF = None
	def get_cov(self):
		"""get covariance matrix for solution; compute if nec"""
		if self._cov is None:
			self._cov = self.sigma2 * la.inv(self.xTx)     #covariance matrix, as array
		#TODO var-cov(b),shd use invpd when availabe
		return self._cov
	cov = property(get_cov, None, None, "parameter covariance matrix")
	def get_standard_errors(self):	# coef. standard errors
		"""compute standard errors for solution"""
		if self._standard_errors is None:
			self._standard_errors = np.sqrt(self.cov.diagonal())
		return self._standard_errors
	se = property(get_standard_errors, None, None, "coefficient standard errors")
	def get_tvals(self):
		if self._tvals is None:
			self._tvals = self.coefs / self.se						# coef. t-statistics
		return self._tvals
	tvals = property(get_tvals, None, None, "t-ratios for parameters")
	def get_pvals(self):
		if self._pvals is None:
			if have_scipy:
				self._pvals = (1-Sstats.t.cdf(np.abs(self.tvals), self.df_e)) * 2	# coef. p-values
			else:
				logging.warn("SciPy unavailable. (Needed to compute p-values.)")
				self._pvals = [np.inf for _ in range(self.ncoefs)]
		return self._pvals
	pvals = property(get_pvals, None, None, "p-values for coef t-ratios, based on Student-t distribution")
	def get_pvalF(self):
		if self._pvalF is None:
			if have_scipy:
				self._pvalF = 1-Sstats.f.cdf(self.F, self.df_r, self.df_e)	# F-statistic p-value
			else:
				logging.warn("SciPy unavailable. (Needed to compute p-values.)")
				self._pvalF = np.inf
		return self._pvalF
	pvalF = property(get_pvalF, None, None, "p-value for F statistic, based on F distribution")
	def get_resids(self):
		return self._resids
	resids = property(get_resids, None, None, "regression residuals")
	def slope_intercept(self, xcol=0):
		"""Return: slope and intercept for variations in one independent variable.
		"""
		X = self.X.A         #as array
		x = X[:,xcol]
		means = X.mean(axis=0)
		means[xcol] = 0
		intercept = np.dot(self.coefs, means)
		slope = self.coefs[xcol]
		return slope, intercept
	def llf(self):
		"""Return model log-likelihood and two information criteria.

		:author: Vincent Nijs & Alan Isaac
		"""
		# Model log-likelihood, AIC, and BIC criterion values 
		nobs, ncoefs, ess = self.nobs, self.ncoefs, self.ess
		llf = -(nobs*1/2)*(1+math.log(2*math.pi)) - (nobs/2)*math.log(ess/nobs)
		aic = -2*llf/nobs + (2*ncoefs/nobs)
		bic = -2*llf/nobs + (ncoefs*math.log(nobs))/nobs
		return llf, aic, bic
	def makeX(self, indep, constant, trend):
		"""Return array, the independent variables,
		which may add a constant and/or a trend.
		"""
		nobs = self.nobs
		#deal with the case of no independent variables (except constant or trend)
		X = list()  #list to hold all independent variables
		if indep is not None:
			indep = np.asarray(indep)
			if len(indep.shape)==1:  #must have been a one dimensional indep
				indep = np.atleast_2d(X).T
			self.indep_names = self.indep_names or list("x%02i"%(i+1) for i in range(indep.shape[1]))
			assert ( nobs == len(indep) )
			self.nvars = indep.shape[1]
			X.append(indep)
		else:
			self.nvars = 0
		self.ncoefs = self.nvars
		#construct constant if requested
		if constant:  #not 0 or False
			constant = constant * np.ones((nobs,1))
			self.ncoefs += 1
			self.indep_names.append('constant')
			X.append(constant)
		#construct trend if requested
		if trend is True:             #default is center at midpoint
			trend = nobs//2
		if trend not in [None, False]:  #allow trend centered at 0
			trend = np.atleast_2d(np.arange(nobs) - trend).T
			self.ncoefs += 1
			self.indep_names.append('trend')
			X.append(trend)
		X = np.hstack( X )
		assert (self.nobs, self.ncoefs) == X.shape
		return X
	def print_results(self):
		"""Return None.  Print results.
		"""
		print self
	def __str__(self):
		# use to print output
		header_template = """
==============================================================================
==============================================================================
Dependent Variable: %(dep_name)s
Method: Least Squares
Date: %(date)s
Time: %(time)s
# obs:              %(nobs)5d
# RHS variables:    %(ncoefs)5d
==============================================================================
""" + 5*"%-15s"%('variable','coefficient','std. Error','t-statistic','pval.') + "\n"
		header_dict = dict(dep_name=self.dep_name, indep_names=self.indep_names,
		date=self.date, time=self.time, nobs=self.nobs, ncoefs=len(self.coefs))
		result_template = "%-15s" + 4*"% -15.5f"
		result = []
		for i in range(len(self.coefs)):
			result.append(result_template % tuple([self.indep_names[i],self.coefs[i],self.se[i],self.tvals[i],self.pvals[i]]) )
		modelstat_template = """
==============================================================================
Model stats
------------------------------------------------------------------------------
Log likelihood       %(llf)10.3f        
R-squared            %(rsq)10.3f             Adjusted R-squared    %(R2adj)10.3f            
F-statistic          %(F)10.3f             Prob (F-statistic)    %(pvalF)10.3f            
AIC criterion        %(aic)10.3f             BIC criterion         %(bic)10.3f
==============================================================================
"""
		modelstat_dict = dict(llf=self.llf, rsq=self.R2, R2adj=self.R2adj, F=self.F,pvalF=self.pvalF,aic=self.aic,bic=self.bic)
		resid_stats_template = """
==============================================================================
Residual stats
==============================================================================
Durbin-Watson stat    % -5.6f' % tuple([self.R2, self.dw()])
Omnibus stat        % -5.6f' % tuple([self.R2adj, omni])    Prob(Omnibus stat)    % -5.6f' % tuple([self.F, omnipv])
JB stat                % -5.6f' % tuple([self.Fpv, JB]) Prob(JB)            % -5.6f' % tuple([ll, JBpv])
Skew     Kurtosis            % -5.6f' % tuple([skew, kurtosis])
==============================================================================
"""
		result = '\n'.join(result).replace('1.#INF','.')
		result = header_template%header_dict + result
		result += modelstat_template%modelstat_dict
		return result

	def rols(self, keep=True):
		"""Return: array(T-ncoefs by ncoefs)

		Compute "recursive OLS" parameter estimates.

		:todo: add standard errors
		"""
		if self._rols_coefs is not None:
			return self._rols_coefs
		from numpy.linalg import solve
		Y, X = np.asmatrix(self.Y), np.asmatrix(self.X)
		nobs, ncoefs = X.shape
		X0 = X[:ncoefs]  #square matrix
		Y0 = Y[:ncoefs]  #square matrix
		#create array to hold parameter estimates
		coef_array = np.empty( (nobs-ncoefs+1, ncoefs) )
		coef_array[0] = solve(X0,Y0).A1
		xTx = X0.T * X0
		xTy = X0.T * Y0
		#get initial parameter estimate (shortest possible data sample)
		#iteratively update parameter estimates
		for i in range(ncoefs,nobs):
			xTx += X[i].T * X[i]
			xTy += X[i].T * Y[i]
			coef_array[i-ncoefs+1] = solve(xTx,xTy).A1
		if keep:
			self._rols_coefs = coef_array
		return coef_array




def linreg(X, Y):
	"""Return (a,b),
	coefficients from the linear regression for y = ax + b. ::

		real, real = linreg(list, list)

	Simple 2 variable linear regression results.
	Basically, it solves ::
	
		 Sxx a + Sx b = Sxy
		  Sx a +  N b = Sy

	where ::

		Sxy = \sum_i x_i y_i
		Sx = \sum_i x_i
		Sy = \sum_i y_i.

	The solution is ::
	
		 a = (Sxy N - Sy Sx)/det
		 b = (Sxx Sy - Sx Sxy)/det

	where ``det = Sxx N - Sx^2``.  In addition, ::
	
		 Var|a| = s^2 |Sxx Sx|^-1 = s^2 | N  -Sx| / det
			|b|       |Sx  N |          |-Sx Sxx|
		 s^2 = {\sum_i (y_i - \hat{y_i})^2 \over N-2}
			 = {\sum_i (y_i - ax_i - b)^2 \over N-2}
			 = residual / (N-2)
		 R^2 = 1 - {\sum_i (y_i - \hat{y_i})^2 \over \sum_i (y_i - \mean{y})^2}
			 = 1 - residual/meanerror

	It also prints a few other data, ::
	
		 N, a, b, R^2, s^2,

	which are useful in assessing the confidence of estimation.

	Only the coefficients of regression line are returned.
	Other informations is sent to stdout to be read later.  

	:author: William Park
	"""
	from math import sqrt
	if len(X) != len(Y):  raise ValueError, 'unequal length'

	N = len(X)
	Sx = Sy = Sxx = Syy = Sxy = 0.0
	for x, y in map(None, X, Y):
		Sx = Sx + x
		Sy = Sy + y
		Sxx = Sxx + x*x
		Syy = Syy + y*y
		Sxy = Sxy + x*y
	det = Sxx * N - Sx * Sx
	a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det

	meanerror = residual = 0.0
	for x, y in map(None, X, Y):
		meanerror = meanerror + (y - Sy/N)**2
		residual = residual + (y - a * x - b)**2
	RR = 1 - residual/meanerror
	ss = residual / (N-2)
	Var_a, Var_b = ss * N / det, ss * Sxx / det
	 
	print "y=ax+b"
	print "N= %d" % N
	print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, sqrt(Var_a))
	print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, sqrt(Var_b))
	print "R^2= %g" % RR
	print "s^2= %g" % ss
	 
	return a, b














class OLSvn:
	"""
	Author: Vincent Nijs (+ ?)

	Email: v-nijs at kellogg.northwestern.edu

	Last Modified: Mon Jan 15 17:56:17 CST 2007
	
	Dependencies: See import statement at the top of this file

	Doc: Class for multi-variate regression using OLS

	For usage examples of other class methods see the class tests at the bottom of this file. To see the class in action
	simply run this file using 'python ols.py'. This will generate some simulated data and run various analyses. If you have rpy installed
	the same model will also be estimated by R for confirmation.

	Input:
		y = dependent variable
		y_varnm = string with the variable label for y
		x = independent variables, note that a constant is added by default
		x_varnm = string or list of variable labels for the independent variables
	
	Output:
		There are no values returned by the class. Summary provides printed output.
		All other measures can be accessed as follows:

		Step 1: Create an OLS instance by passing data to the class

			m = ols(y,x,y_varnm = 'y',x_varnm = ['x1','x2','x3','x4'])

		Step 2: Get specific metrics

			To print the coefficients: 
				>>> print m.b
			To print the coefficients p-values: 
				>>> print m.p
	
	"""

	def __init__(self,y,x,y_varnm = 'y',x_varnm = ''):
		"""
		Initializing the ols class. 
		"""
		self.y = y
		self.x = c_[ones(x.shape[0]),x]
		self.y_varnm = y_varnm
		if not isinstance(x_varnm,list): 
			self.x_varnm = ['const'] + list(x_varnm)
		else:
			self.x_varnm = ['const'] + x_varnm

		# Estimate model using OLS
		self.estimate()

	def estimate(self):

		# estimating coefficients, and basic stats
		self.inv_xx = inv(dot(self.x.T,self.x))
		xy = dot(self.x.T,self.y)
		self.b = dot(self.inv_xx,xy)					# estimate coefficients

		self.nobs = self.y.shape[0]						# number of observations
		self.ncoef = self.x.shape[1]					# number of coef.
		self.df_e = self.nobs - self.ncoef				# degrees of freedom, error 
		#TODO: fix!
		self.df_r = self.ncoef - 1						# degrees of freedom, regression 

		self.e = self.y - dot(self.x,self.b)			# residuals
		self.sse = dot(self.e,self.e)/self.df_e			# SSE
		self.se = sqrt(diagonal(self.sse*self.inv_xx))	# coef. standard errors
		self.t = self.b / self.se						# coef. t-statistics
		self.p = (1-Sstats.t.cdf(abs(self.t), self.df_e)) * 2	# coef. p-values

		self.R2 = 1 - self.e.var()/self.y.var()			# model R-squared
		self.R2adj = 1-(1-self.R2)*((self.nobs-1)/(self.nobs-self.ncoef))	# adjusted R-square

		self.F = (self.R2/self.df_r) / ((1-self.R2)/self.df_e)	# model F-statistic
		self.Fpv = 1-Sstats.f.cdf(self.F, self.df_r, self.df_e)	# F-statistic p-value

	def dw(self):
		"""
		Calculates the Durbin-Waston statistic
		"""
		de = diff(self.e,1)
		dw = dot(de,de) / dot(self.e,self.e);

		return dw

	def omni(self):
		"""
		Omnibus test for normality
		"""
		return Sstats.normaltest(self.e) 
	
	def JB(self):
		"""
		Calculate residual skewness, kurtosis, and do the JB test for normality
		"""

		# Calculate residual skewness and kurtosis
		skew = Sstats.skew(self.e) 
		kurtosis = 3 + Sstats.kurtosis(self.e) 
		
		# Calculate the Jarque-Bera test for normality
		JB = (self.nobs/6) * (square(skew) + (1/4)*square(kurtosis-3))
		JBpv = 1-Sstats.chi2.cdf(JB,2);

		return JB, JBpv, kurtosis, skew

	def ll(self):
		"""
		Calculate model log-likelihood and two information criteria
		"""
		
		# Model log-likelihood, AIC, and BIC criterion values 
		ll = -(self.nobs*1/2)*(1+np.log(2*math.pi)) - (self.nobs/2)*np.log(np.dot(self.e,self.e)/self.nobs)
		aic = -2*ll/self.nobs + (2*self.ncoef/self.nobs)
		bic = -2*ll/self.nobs + (self.ncoef*np.log(self.nobs))/self.nobs

		return ll, aic, bic
	
	def summary(self):
		"""
		Printing model output to screen
		"""

		# local time & date
		t = time.localtime()

		# extra stats
		ll, aic, bic = self.ll()
		JB, JBpv, skew, kurtosis = self.JB()
		omni, omnipv = self.omni()

		# printing output to screen
		print '\n=============================================================================='
		print "Dependent Variable: " + self.y_varnm
		print "Method: Least Squares"
		print "Date: ", time.strftime("%a, %d %b %Y",t)
		print "Time: ", time.strftime("%H:%M:%S",t)
		print '# obs:				%5.0f' % self.nobs
		print '# variables:		%5.0f' % self.ncoef 
		print '=============================================================================='
		print 'variable		coefficient		std. Error		t-statistic		prob.'
		print '=============================================================================='
		for i in range(len(self.x_varnm)):
			print """% -5s			% -5.6f		% -5.6f		% -5.6f		% -5.6f""" % tuple([self.x_varnm[i],self.b[i],self.se[i],self.t[i],self.p[i]]) 
		print '=============================================================================='
		print 'Models stats							Residual stats'
		print '=============================================================================='
		print 'R-squared			% -5.6f			Durbin-Watson stat	% -5.6f' % tuple([self.R2, self.dw()])
		print 'Adjusted R-squared	% -5.6f			Omnibus stat		% -5.6f' % tuple([self.R2adj, omni])
		print 'F-statistic			% -5.6f			Prob(Omnibus stat)	% -5.6f' % tuple([self.F, omnipv])
		print 'Prob (F-statistic)	% -5.6f			JB stat				% -5.6f' % tuple([self.Fpv, JB])
		print 'Log likelihood		% -5.6f			Prob(JB)			% -5.6f' % tuple([ll, JBpv])
		print 'AIC criterion		% -5.6f			Skew				% -5.6f' % tuple([aic, skew])
		print 'BIC criterion		% -5.6f			Kurtosis			% -5.6f' % tuple([bic, kurtosis])
		print '=============================================================================='


def rolsf(x, y, p, th, lam):
	"""Return: new parameter estimate and covariance matrix:

	Recursive ordinary least squares for single output case,
	including a forgetting factor.
	This ROLS function uses the Matrix Inversion Lemma (MIL)
	to calculate the update to the covariance matrix.  
	This is known to be somewhat unstable, numerically, but works 'well 
	enough' for many problems.  The Bierman UD or Givens square root methods 
	are more stable, but somewhat more complicated to program.

	Enter with x(N,1) = input, y = output, p(N,N) = covariance,
	th(N,1) = estimate,  lam = forgetting factor.

	:license: BSD
	:author: J. C. Hassler
	:since: 12-feb-95 (Originally written in Matlab.)
	:date: 2-oct-07 (Translated to Python)
	"""
	a = np.inner(p,x)
	g = 1./(np.inner(x,a)+lam)
	k = g*a
	e = y-np.inner(x,th)
	th += k*e
	p = (p-g*np.outer(a,a))/lam
	return th, p
 
