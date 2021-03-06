"""A collection of unit root tests for SciPy.

Example use::

	rw = numpy.cumsum( numpy.random.rand(100) )
	#print ADF results for lag=4
	adf_ls(rw, 4, prt=True)
	#print ADF results for lags up to lag=4
	adf(rw, 4)

:note: Based on GAUSS code by Alan G. Isaac and David Rapach.  (KPSS test missing.)
:note: written for: Python 2.5 and SciPy
:note: Should work fine without SciPy if you have NumPy
:license: `MIT license`_
:see: tseries.py
:see: pytrix.py
:since: 2004-08-10
:see: `current location`_
:contact: aisaac AT american.edu http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm

.. _`current location`: http://econpy.googlecode.com/svn/trunk/pytrix/unitroot.py
.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import division, absolute_import
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '2007-09-10'

import logging
logging.basicConfig(level=logging.WARN)

import numpy as np
from .ls import OLS
from .tseries import varlags

adf_cv1 = """
One-sided test of H0: Unit root vs. H1: Stationary
Approximate asymptotic critical values (t-ratio):
------------------------------------------------------------
  1%      5%      10%      Model
------------------------------------------------------------
-2.56   -1.94   -1.62     Simple ADF (no constant or trend)
-3.43   -2.86   -2.57     ADF with constant (no trend)
-3.96   -3.41   -3.13     ADF with constant & trend
------------------------------------------------------------"""


def adf_ls(y, p, prt=False):
	"""Return: `results`, a dictionary of OLS instances,
	one instance for each regression type
	('noconstant', 'constant','constant_trend').

	:Parameters:
		y : sequence
			N-element sequence (the univariate time series of interest)
		p : scalar
			lag (autocorrelation order)
		prt :  boolean
			prt=True to print results
	:Output: `results`, dictionary of OLS instances.
	:requires: 	function 'varlags' (imported fr tseries)
	:requires: 	class 'OLS' (import from ls)
	:see: Russell Davidson and James G. MacKinnon,
	      _Estimation and Inference in Econometrics_
	      (New York: Oxford, 1993)
	      See references therein for original sources
	:since: 2004-08-10
	:date:   1 June 2010
	:contact: aisaac AT american.edu
	"""
	y = np.squeeze( np.asarray(y) )  #squeeze to 1d if possible
	if len(y.shape)>1:
		raise ValueError('Input array should be 1d')
	#dy and addx are 2d
	dy = np.diff(y).reshape((-1,1))  #first difference
	rhs = y[p:-1].reshape((-1,1))  #lag level
	if p > 0:
		dy, dylags = varlags(dy, p)    # generating lags
		rhs = np.concatenate([rhs, dylags], 1)
	T = dy.shape[0]                      # effective number of observations
	#THREE VERSIONS of regression
	results = dict()  #holds the three sets of regression results
	#1. no constant
	logging.info('noconstant')
	results['noconstant'] =  OLS(dy, rhs, constant=None)
	#2. add constant to regressors
	logging.info('constant')
	results['constant'] =  OLS(dy, rhs)
	#3. add (midpt centered) trend to regressors
	logging.info('constant_trend')
	results['constant_trend'] =  OLS(dy, rhs, trend=T//2)
	if prt :
		print(adf_cv1)
		print """
ADF results for %s lags
------------------------------------------------------------
                 ADF regression coefficients
                       (t-ratio)
              For model including the following:
              ----------------------------------
              No Constant  Constant    Trend
   RHS var    No Trend     No Trend    Constant
--------------------------------------------------""" % (p,)
		ids = ('noconstant', 'constant', 'constant_trend')
		fmt_b = "%11.3f"
		fmt_t = "%11s"
		#print results for lagged level
		print 'x(-1)'.rjust(10) + " "*3,
		print (fmt_b*3)%tuple( results[id].coefs[0] for id in ids )
		print " "*13,
		print (fmt_t*3)%tuple( "(%1.2f)"%(results[id].tvals[0]) for id in ids )
		#print results for lagged differences
		for i in range(1,p+1) :
			print ('dx(-%i)'%(i,)).rjust(10) + " "*3,
			print (fmt_b*3)%tuple( results[id].coefs[i] for id in ids )
			print " "*13,
			print (fmt_t*3)%tuple( "(%1.2f)"%(results[id].tvals[i]) for id in ids )
		#print results for constant
		print 'Constant'.rjust(10) + " "*(3+11),     #pad for skipping 'noconstant'
		print (fmt_b*2)%tuple( results[id].coefs[p+1] for id in ids[1:] )
		print " "*(10+3+11),
		print (fmt_t*2)%tuple( "(%1.2f)"%(results[id].tvals[p+1]) for id in ids[1:] )
		#print results for trend
		print 'Trend'.rjust(10) + " "*(3+2*11),
		print (fmt_b)%tuple( results[id].coefs[-1] for id in ids[-1:] )
		print " "*(10+3+2*11),
		print (fmt_t)%tuple( "(%1.2f)"%(results[id].tvals[p+2]) for id in ids[-1:] )
		#print sum of squared residuals
		print 'ESS'.rjust(10) + " "*3,
		print (fmt_b*3)%tuple( results[id].ess for id in ids )
		print """------------------------------------------------------------
Note: trend is centered at sample midpoint.
Note: coefficient on constant depends on trend centering.
Note: ESS = error sum of squares (i.e., sum of squared resids)."""
		#TODO: Could use SSR for Dickey Fuller (1981) Phi tests */
	return results


def adf(y, p):
	"""Return: None.
	Prints augmented Dickey-Fuller results for lags up to lag p.

	:Parameters:
		y : sequence
			N-element sequence (the time series of interest)
		p : scalar
			maximum lag (autocorrelation order)
	:requires: function `adf_ls` (provided)
	:requires: 	function 'varlags' (imported fr tseries)
	:requires: 	class 'OLS' (import from ls)
	:see: Russell Davidson and James G. MacKinnon,
	      _Estimation and Inference in Econometrics_
	      (New York: Oxford, 1993)
	      See references therein for original sources
	      See p.708, table 20.1 for critical values
	:see: Harris, 1992, Economics Letters
	:since: 2004-08-10
	:date:   10 Sep 2007
	:contact: aisaac AT american.edu
	"""
	#local obs,i,b,ty,temp,oldcv,oldnv;
	obs = np.shape(y)[0]
	print adf_cv1  #table of critical values
	print """You began with a series of %s observations, in which case
Harris (1992) recommends using %s lags.""" % (obs,int(12*(obs/100)**(1/4)))
	print """
------------------------------------------------------------
               ADF coef on lagged level
                       (t-ratio)
               For model including the following:
               ----------------------------------
      Lags     No Constant  Constant    Constant        Obs
               No Trend     No Trend    & Trend
------------------------------------------------------------"""
	ids = ('noconstant', 'constant', 'constant_trend')
	fmt_b = "%11.3f"*3
	fmt_t = "%11s"*3
	for i in range(p+1) :
		results = adf_ls(y, i, prt=False)  #dict of results: id -> OLS instance
		print str(i).rjust(10) + " "*3,
		print fmt_b%tuple( results[id].coefs[0] for id in ids ),
		print "%11d"%results['constant'].nobs
		print " "*13,
		print fmt_t%tuple( "(%1.2f)"%(results[id].tvals[0]) for id in ids )
		print
	print "------------------------------------------------------------"




"""Someone should translate this KPSS function asap!
Proc            : KPSS
Author          : David Rapach
Last revised    : 27 May 1996
Input           : y -- (T x 1) vector of obs on variable of interest
                : p -- specified max order of autocorrelation
Output          : Prints KPSS statistics
Globals         : None
Reference       : Denis Kwiatowski, Peter C.B. Phillips, Peter Schmidt,
                      and Tongcheol Shin, "Testing the null hypothesis of
                      stationarity against the alternative of a unit root:
                      How sure are we that economic series have a unit
                      root?" _Journal of Econometrics_ 54 (Oct./Dec.
                      1992): 159-178
Notes           : KPSS(trend) based on y(t)=a+bt+e(t) -- trend stationarity
                  KPSS(level) based on y(t)=a+e(t)    -- level stationarity
***************************************************************************/
proc(0)=kpss(y,l);
    local T,trend,X,b,e,g0,p,g,i,w,s2,S,ei,etathat,etamhat,lag,
          eta,oldnv;

    /* Level-stationary test */

    T=rows(y);              @ # of obs @
    X=np.ones(T,1);            @ RHS var @
    b=y/X;                  @ OLS estimates @
    e=y-X*b;                @ OLS resids @
    g0=e'e/T;               @ gamma_0=(1/T)sum[e(t)^2] @
    etamhat=zeros(l+1,1);
    p=1;
    do until p>l;
        g=zeros(p,1);       @ autocovs @
        i=1;
        do until i>p;
            g[i,1]=(e[1+i:T,1]'e[1:T-i,1])/T;@ gamma_i=(1/T)sum[e(t)e(t-i)] @
            i=i+1;
        endo;
        w=zeros(p,1);
        i=1;
        do until i>p;
            w[i,1]=(p+1-i)/(p+1);   @ Bartlett window weight @
            i=i+1;
        endo;
        s2=g0+2*w'g;                @ consistent error variance estimate @
        S=zeros(T,1);               @ resid partial sum process @
        i=1;
        do until i>T;
            ei=e[1:i,.];
            S[i,.]=sumc(ei);        @ S(i)=sum[e(i)] @
            i=i+1;
        endo;
        etamhat[1,.]=(1/(g0*T^2))*S'S;      @ KPSS eqn (13), l=0 @
        etamhat[p+1,.]=(1/(s2*T^2))*S'S;    @ KPSS eqn (13) @
        p=p+1;
    endo;

    /* Trend-stationary test */

    trend=seqa(1,1,T);      @ linear time trend @
    X=np.ones(T,1)~trend;      @ regressor matrix @
    b=y/X;                  @ OLS estimates @
    e=y-X*b;                @ OLS resids @
    g0=e'e/T;               @ gamma_0=(1/T)sum[e(t)^2] @
    etathat=zeros(l+1,1);
    p=1;
    do until p>l;
        g=zeros(p,1);       @ autocovs @
        i=1;
        do until i>p;
            g[i,1]=(e[1+i:T,1]'e[1:T-i,1])/T;@ gamma_i=(1/T)sum[e(t)e(t-i)] @
            i=i+1;
        endo;
        w=zeros(p,1);
        i=1;
        do until i>p;
            w[i,1]=(p+1-i)/(p+1);   @ Bartlett window weight @
            i=i+1;
        endo;
        s2=g0+2*w'g;                @ consistent error variance estimate @
        S=zeros(T,1);               @ resid partial sum process @
        i=1;
        do until i>T;
            ei=e[1:i,.];
            S[i,.]=sumc(ei);        @ S(i)=sum[e(i)] @
            i=i+1;
        endo;
        etathat[1,.]=(1/(g0*T^2))*S'S;      @ KPSS eqn (17), l=0 @
        etathat[p+1,.]=(1/(s2*T^2))*S'S;    @ KPSS eqn (17) @
        p=p+1;
    endo;
    format 8,4;
    "One-sided test of H0: Stationary vs. H1: Unit root";?;
    "Approximate asymptotic critical values";
    "--------------------------------------------------";
    "              10%     5%      1%";
    "--------------------------------------------------";
    "Level        0.347   0.463   0.739";
    "Trend        0.119   0.146   0.216";
    "--------------------------------------------------";?;
    lag=seqa(0,1,l+1);
    eta=etamhat~etathat;
    oldnv=__fmtnv;
    __fmtnv="*.*lg"~8~3;
    "KPSS stats";
    "--------------------------------------------------";
    "      Lag     Level    Trend";
    "--------------------------------------------------";
    i=1;
    do until i>l+1;
        call printfmt(lag[i,.],1);"    " eta[i,.];
        i=i+1;
    endo;
    "--------------------------------------------------";
    "Obs";;call printfmt(T,1);
    __fmtnv=oldnv;
endp;
"""
