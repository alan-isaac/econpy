'''Various utilities useful for economists.
Most are lightweight, in the sense that they do not depend on an array package.

:see: `pytrix.py <http://www.american.edu/econ/pytrix/pytrix.py>`
:see: `pyGAUSS.py <http://www.american.edu/econ/pytrix/pyGAUSS.py>`
:see: poly.py
:see: tseries.py
:see: unitroot.py
:see: pytrix.py
:see: IO.py
:warning: Some of William Park's functions did not correctly retab,
          and I have not had time to check all of them.
          Please test before using.  (Always a good idea of course.)
:note: Please include proper attribution should this code be used in a research project or in other code.
:see: The code below by William Park and more can be found in his `Simple Recipes in Python`_
:author: Alan G. Isaac, except where otherwise specified.
:copyright: 2005 Alan G. Isaac, except where another author is specified.
:license: `MIT license`_ except where otherwise specified.
:since: 2004-08-04

.. _`Simple Recipes in Python`: http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
from __future__ import division
from __future__ import absolute_import
__docformat__ = "restructuredtext en"

import random, math, operator
import types
import sys,os
import logging

have_numpy = False
try:
	import numpy
	from numpy import linalg
	have_numpy = True
except ImportError:
	logging.info("numpy not available")


#class OLS
#--------------------------------------------------------------------
#Methods:        : 
#                  calcCov() -- returns covariance matrix for soln
#                  calcSE() -- returns standard errors for soln
#                  calcTval() -- returns t-ratios for soln
#--------------------------------------------------------------------
class OLS:
	'''Least squares estimates.
	
	:globals: Requires function 'varlags' (provided)
	:Ivariables:
		`soln` : float
			the least squares solution
		`nobs` : int
			rows(dep)
		`xTx` : array
			KxK array (indep' * indep)
		`xTy` : array
			Kx1 array (indep' * dep)
		`resids` : array
			Tx1 array (dep - indep * soln)
		`sig2` : float
			(resids' * resids)/(T-K)
	:see: Russell Davidson and James G. MacKinnon,
          _Estimation and Inference in Econometrics_
          (New York: Oxford, 1993)
	:see: http://www.scipy.org/Cookbook/OLS different approach but shared goals
	:date: 2005-12-08
	:since: 2004-08-11
	:author: Alan G. Isaac
	'''
	def __init__(self,dep,indep):
		'''
		:Parameters:
			`dep` : array
				(T x 1) array, the LHS variable
			`indep` : array
				(T x K) array, the RHS variables
		'''
		if have_numpy:
			self.soln, self.SSR = linalg.lstsq(indep,dep)[:2]  #OLS estimates
			self.nobs=numpy.shape(dep)[0]
		#note: careful if use numarray: use copy to offset matrix multiply bug in numpy<=1
		#http://sourceforge.net/mailarchive/forum.php?thread_id=5307744&forum_id=4890
		X = numpy.mat(indep)
		Y = numpy.mat(numpy.asarray(dep).reshape((-1,1)))  #TODO single equation only
		self.xTx = X.T*X
		self.xTy = X.T*Y
		self.resids = Y - X*numpy.mat(self.soln)  #TODO single equation only
		self.sig2=self.SSR[0]/(self.nobs-X.shape[1])        # s2 estimate
	def calcCov(self):
		'''compute covariance matrix for solution'''
		return (self.sig2*numpy.linalg.inv(self.xTx))      #TODO var-cov(b),shd use invpd when availabe
	def calcSE(self):
		'''compute standard errors for solution'''
		return numpy.sqrt(numpy.diagonal(self.calcCov())).reshape((-1,1))          # std errs
	def get_resids(self):
		return self.resids
	def calcTval(self):
		'''compute t-ratios for solution'''
		return (self.soln/self.solnSE)



def linreg(X, Y):
	"""Linear regression of y = ax + b. ::

		real, real = linreg(list, list)

	Returns coefficients to the regression line "y=ax+b" from x[] and
	y[].  Basically, it solves ::
	
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

	Only the coefficients of regression line are returned,
	since they are usually what I want.
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














class ols:
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
		self.df_r = self.ncoef - 1						# degrees of freedom, regression 

		self.e = self.y - dot(self.x,self.b)			# residuals
		self.sse = dot(self.e,self.e)/self.df_e			# SSE
		self.se = sqrt(diagonal(self.sse*self.inv_xx))	# coef. standard errors
		self.t = self.b / self.se						# coef. t-statistics
		self.p = (1-stats.t.cdf(abs(self.t), self.df_e)) * 2	# coef. p-values

		self.R2 = 1 - self.e.var()/self.y.var()			# model R-squared
		self.R2adj = 1-(1-self.R2)*((self.nobs-1)/(self.nobs-self.ncoef))	# adjusted R-square

		self.F = (self.R2/self.df_r) / ((1-self.R2)/self.df_e)	# model F-statistic
		self.Fpv = 1-stats.f.cdf(self.F, self.df_r, self.df_e)	# F-statistic p-value

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
		return stats.normaltest(self.e) 
	
	def JB(self):
		"""
		Calculate residual skewness, kurtosis, and do the JB test for normality
		"""

		# Calculate residual skewness and kurtosis
		skew = stats.skew(self.e) 
		kurtosis = 3 + stats.kurtosis(self.e) 
		
		# Calculate the Jarque-Bera test for normality
		JB = (self.nobs/6) * (square(skew) + (1/4)*square(kurtosis-3))
		JBpv = 1-stats.chi2.cdf(JB,2);

		return JB, JBpv, kurtosis, skew

	def ll(self):
		"""
		Calculate model log-likelihood and two information criteria
		"""
		
		# Model log-likelihood, AIC, and BIC criterion values 
		ll = -(self.nobs*1/2)*(1+log(2*pi)) - (self.nobs/2)*log(dot(self.e,self.e)/self.nobs)
		aic = -2*ll/self.nobs + (2*self.ncoef/self.nobs)
		bic = -2*ll/self.nobs + (self.ncoef*log(self.nobs))/self.nobs

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
			print '''% -5s			% -5.6f		% -5.6f		% -5.6f		% -5.6f''' % tuple([self.x_varnm[i],self.b[i],self.se[i],self.t[i],self.p[i]]) 
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
