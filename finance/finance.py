"""
Finance functions contributed by Skipper Seabold.
"""

import numpy as np

def _discf(rate, pmts, dates):
    '''
    Convenience function for calculating discrete time dpv and its derivative.
    '''
    from datetime import date
    dcf=[]
    dcfprime=[]
    if isinstance(dates[0],date):
        for i,cf in enumerate(pmts):
            d=dates[i]-dates[0]
            dcf.append(cf*(1+rate)**(-d.days/365.))
            dcfprime.append((-d.days/365.)*cf*(1+rate)**(-d.days/365. - 1))
        return np.add.reduce(dcf),np.add.reduce(dcfprime)
    for i,cf in enumerate(pmts):
        if i==0:
            dcf.append(cf)
        else:
            dcf.append(cf*(1+rate)**(-dates[i-1]/365.))
            dcfprime.append((-dates[i-1]/365.)*cf*(1+rate)**\
            (-dates[i-1]/365.-1))
    return np.add.reduce(dcf),np.add.reduce(dcfprime)

def xirr(pmts, dates, guess=.10, maxiter=100, tol=1.48e-8):
    '''
    IRR function that accepts irregularly spaced cash flows

    Parameters
    ----------
    values: array_like
          Contains the cash flows including the initial investment
    dates: array_like
          Contains the dates of payments as in the form (year, month, day)

    Returns: Float
          Internal Rate of Return

    Examples
    --------------
    dates=[[2008,2,5],[2008,7,5],[2009,1,5]]
    for i, dt in enumerate(dates):
        dates[i]=date(*dt) 
    pmts=[-2750,1000,2000]
    print xirr(pmts,dates)
 
    or

    dates==[151,335]
    pmt=[-2750,100,2000]
    print xirr(pmts,dates)

    Notes
    -----
    In general the xirr is the solution to

    .. math:: \sum_{t=0}^M{\frac{v_t}{(1+xirr)^{(date_t-date_0)/365}}} = 0

    To Do
    -----
    Get rid of reliance on date type or days difference.
    Write a *simple* date parser?
    Add tests. What behavior for only one cashflow?

    '''
#   how to do it with scipy, _discf doesn't need derivative   
#    f = lambda x: _discf(x, pmts, dates)
#    try: 
#        from scipy.optimize import newton
#        print "scipy did it"
#        return newton(f, guess)
#    except:
#        pass

#   Newton-Raphson iterations
    x0 = guess
    for iter in range(maxiter):
        func,funcp = _discf(x0,pmts,dates)
        if funcp == 0:
            print "Warning: Stopped on zero-derivative.\n"
            print "Solution set to current guess %s." % (x0)
            return x0
        x = x0 - func/funcp
        if abs(x-x0) < tol:
            return x
        x0 = x
    raise RuntimeError, "Failed to converge after %d iterations, returnging %s." % (maxiter, x)


if __name__=="__main__":
    print "xirr functions"    
    dates=[[2008,2,5],[2008,7,5],[2009,1,5]]
    from datetime import date
    for i,dt in enumerate(dates):
         dates[i]=date(*dt)
    pmts=[-2750,1000,2000]
    print xirr(pmts,dates)
    print
    dates2=[151,335]
    print xirr(pmts,dates2)
