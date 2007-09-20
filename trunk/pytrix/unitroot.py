'''A collection of unit root tests for SciPy.

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
'''
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '2007-08-10'

import numpy as N
from .ls import OLS
from .tseries import varlags



#adf_ls
#Input           : y   -- (N x 1) vector, the time series of interest
#                  p   -- scalar, maximum lag (max autocorr order)
#                  prt -- boolean, prt=True to print results
#Output          : b   -- coefs from ADF regression
#                  t   -- t-stats from ADF regression
#                  obs -- scalar, rows(y)-(p+1)
#                : Prints augmented Dickey-Fuller t-stats
#Globals         : None
#Notes           : Requires function 'varlags' (imported fr tseries)
#                : Requires function 'ols' (provided)
#References      : Russell Davidson and James G. MacKinnon,
#                      _Estimation and Inference in Econometrics_
#                      (New York: Oxford, 1993)
#                      See references therein for original sources
#Authors         : Alan G. Isaac
#Last revised    : 10 Aug 2004
#--------------------------------------------------------------------
def adf_ls(y,p,prt=False):
	#local addx,dy,dylags,reportmat,T,b,e,SSE,covb,seb
	y=N.reshape(y,(-1,1))
	addx=y[p:-1]                  # lag level
	dy=y[1::]-y[:-1]                       # differencing
	if p > 0:
		dy,dylags=varlags(dy,p)    # generating lags
		addx=N.concatenate([addx,dylags],1)
	T=N.shape(dy)[0]                      # number of observations
	reportmat=[[None for i in range(p+4)] for i in range(6)]   #avoid shallow copies
	results = dict()
	#no constant
	result = OLS(dy, addx, constant=None)
	reportmat[0][0:p+1] = N.ravel(result.coefs)
	reportmat[0][p+3] = result.ess
	reportmat[1][0:p+1] = N.ravel(result.se)
	results['noconstant'] = result
	# adds constant to regressors
	result = OLS(dy,addx)
	reportmat[2][0:p+2] = result.coefs
	reportmat[2][p+3] = result.ess
	reportmat[3][0:p+2] = result.se
	results['constant'] = result
	# add trend to regressors
	result = OLS(dy,addx, trend=T//2)
	reportmat[4][0:p+3] = result.coefs
	reportmat[4][p+3] = result.ess
	reportmat[5][0:p+3] = result.se
	results['constant_trend'] = result
	reportmat = zip(*reportmat)
	if prt :
		print '''
ADF results for %s lags
------------------------------------------------------------
              ADF regression coefficients
                     (t-ratio)
              For model including the following:
              ----------------------------------
              No Constant  Constant    Trend
   RHS var    No Trend     No Trend    Constant
--------------------------------------------------''' % (p,)
		print 'x(-1)'.rjust(10) + '%s'*3 % tuple(map(lambda x:('%1.3g'%(x,)).center(15),reportmat[0][0:6:2]))
		print ''.rjust(10) + '%s'*3 % tuple(map(lambda x:('(%1.3g)'%(x,)).center(15),reportmat[0][1:6:2]))
		for i in range(1,p+1) :
			print ('dx(-%i)'%(i,)).rjust(10) + '%s'*3 % tuple(map(lambda x:('%1.3g'%(x,)).center(15),reportmat[i][0:6:2]))
			print ''.rjust(10) + '%s'*3 % tuple(map(lambda x:('(%1.3g)'%(x,)).center(15),reportmat[i][1:6:2]))
		print 'Constant'.rjust(10) + ' '*15 + '%s'*2 % tuple(map(lambda x:('%1.3g'%(x,)).center(15),reportmat[p+1][2:6:2]))
		print ''.rjust(10) + ' '*15 + '%s'*2 % tuple(map(lambda x:('(%1.3g)'%(x,)).center(15),reportmat[p+1][3:6:2]))
		print 'Trend'.rjust(10) + ' '*(15*2) + '%s' % tuple(map(lambda x:('%1.3g'%(x,)).center(15),reportmat[p+2][4:6:2]))
		print ''.rjust(10) + ' '*(15*2) + '%s' % tuple(map(lambda x:('(%1.3g)'%(x,)).center(15),reportmat[p+2][5:6:2]))
		print 'SSR'.rjust(10) + '%s'*3 % tuple(map(lambda x:('%1.3g'%(x,)).center(15),reportmat[p+3][0:6:2]))
		print '''------------------------------------------------------------
Note: Final line is sum of squared residuals.
Note: coefficient on constant depends on trend centering.'''
		# Could use SSR for Dickey Fuller (1981) Phi tests */
	return results


#adf:
#Input           : y -- (N x 1) array, the time series of interest
#                  p -- scalar, maximum lag (max autocorr order)
#Output          : Prints augmented Dickey-Fuller t-stats
#Globals         : 
#Notes           : Requires function 'varlags' (imported fr tseries)
#                : Requires function 'adf_ls()' (provided)
#References      : Russell Davidson and James G. MacKinnon,
#                      _Estimation and Inference in Econometrics_
#                      (New York: Oxford, 1993)
#                      See references therein for original sources
#                      See p.708, table 20.1 for critical values
#                  Harris, 1992, Economics Letters
#Author          : Alan G. Isaac 
#Last revised    : 7 Aug 2004
#--------------------------------------------------------------------
def adf(y,p):
	#local obs,i,b,ty,temp,oldcv,oldnv;
	obs=N.shape(y)[0]
	print '''
One-sided test of H0: Unit root vs. H1: Stationary
Approximate asymptotic critical values (t-ratio):
------------------------------------------------------------
  1%      5%      10%      Model
------------------------------------------------------------
-2.56   -1.94   -1.62     Simple ADF (no constant or trend)
-3.43   -2.86   -2.57     ADF with constant (no trend)
-3.96   -3.41   -3.13     ADF with constant & trend
------------------------------------------------------------'''
	print '''You began with a series of %s observations, in which case
Harris (1992) recommends using %s lags.''' % (obs,int(12*(obs/100)**(1/4)))
	print '''
------------------------------------------------------------
               ADF coef on lagged level
                       (t-ratio)
               For model including the following:
               ----------------------------------
      Lags     No Constant  Constant    Constant        Obs
               No Trend     No Trend    & Trend
------------------------------------------------------------'''
	ids = ('noconstant', 'constant', 'constant_trend')
	fmt_b = "%11.3f"*3
	fmt_t = "%11s"*3
	for i in range(p+1) :
		results = adf_ls(y,i,False)
		print "%10d"%(i) + " "*3,
		print fmt_b%tuple( results[id].coefs[0] for id in ids ),
		print "%11d"%results['constant'].nobs
		print " "*13,
		print fmt_t%tuple( "(%1.2g)"%(results[id].se[0]) for id in ids )
		print
		#print str(i).rjust(10) + '%s'*3 % tuple(map(lambda x:('%1.2g'%(x,)).center(15),reportmat[0][0:6:2])) + str(obs)
		#print ''.rjust(10) + '%s'*3 % tuple(map(lambda x:('(%1.2g)'%(x,)).center(15),reportmat[0][1:6:2]))
	print "------------------------------------------------------------"




'''Someone should translate this KPSS function asap!
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
    X=N.ones(T,1);            @ RHS var @
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
    X=N.ones(T,1)~trend;      @ regressor matrix @
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
'''
