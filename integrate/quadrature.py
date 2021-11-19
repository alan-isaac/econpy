'''Provide some quadrature related classes and functions.

:date: 2008-08-12
:since: 2008-08-08
:copyright: Alan G. Isaac, except where another author is specified.
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '2008-08-12'

from ..optimize.iterate import IterativeProcess, AbsDiff


def riemann_p(f, p, tags):
    """Return float,
    a Riemann sum for the partition `p`."""
    x1x2 = zip(p[:-1],p[1:])
    if tags == 'left':
        result = sum( (x2-x1)*f(x1) for x1,x2 in x1x2 )
    elif tags == 'right':
        result = sum( (x2-x1)*f(x2) for x1,x2 in x1x2 )
    elif tags in ('center','middle'):
        result = sum( (x2-x1)*f((x1+x2)/2.0) for x1,x2 in x1x2 )
    elif tags == 'trapz': #delay division by 2
        result = sum( (x2-x1)*(f(x1)+f(x2)) for x1,x2 in x1x2 )
    else:
        raise ValueError("Unknown tag type: %s" % (tags))
    if tags == 'trapz':
        result *= 0.5
    return result

def riemann_n(f, a, b, n, tags):
    """Return float,
    a Riemann sum for `n` equal intervals."""
    dx = (b - a) / float(n)
    if tags in ('left','right','trapz'):
        pt = a + dx
    elif tags in ('middle','center'):
        pt = a + dx/2.0
    else:
        raise ValueError("unknown tag type"%(tags))
    result = sum(f(pt + i*dx) for i in range(n-1) )
    if tags == 'left':
        result += f(a)
    elif tags == 'right':
        result += f(b)
    elif tags == 'trapz':
        result += (f(a) + f(b)) / 2.0
    else:   # tags in ('middle','center'):
        result += f(b - dx/2.0)
    result *= dx
    return result

def iterative_trapz(f, a, b, maxiter=100, prt=False):
    """Return float,
    quadrature of `f` based on iterative trapezoid rule.

    :requires: `riemann_n`
    """
    refine = True; n = 1; iter = 0
    area = (b - a) * (f(a)+f(b)) / 2.0
    while(refine and iter<maxiter):
        area_new = 0.5*(area + riemann_n(f, a, b, n, 'middle'))
        n *= 2; iter += 1
        diff = abs(area_new - area)
        if prt:
            print("Old: %f \t New: %f \t Change: %f"%(area,area_new,diff))
        refine = diff > 1.5e-8
        area = area_new
    return area

class IterativeTrapz(IterativeProcess):
    def __init__(self, f, a, b, criterion=None, reportfreq=0):
        '''Return: None.
        Initialize the quadrature problem.
        Set a criterion.
        '''
        self.f = f
        self.bounds = a, b
        self.iteration = 0
        self.ntrapz = 1
        self.value = (b - a) * (f(a)+f(b)) / 2.0
        self.history = [ self.value ]
        self.set_criterion(criterion)
        self.reportfreq = reportfreq
    #users usually override the following methods
    def default_criterion(self):
        return AbsDiff(precision=1.5e-8, maxiter=100)
    #users must implement the following methods
    def iterate(self):
        """Return float,
        quadrature of `f` based on iterative trapezoid rule.
        Used by `next`.

        :requires: `riemann_n`
        """
        f = self.f
        a, b = self.bounds
        ntrapz = self.ntrapz
        area_old = self.history[-1]
        area_new = 0.5*(area_old + riemann_n(f, a, b, ntrapz, 'middle'))
        self.ntrapz *= 2
        return area_new
    def get_testinfo(self, value=None, iteration=0):
        '''Should return: testinfo usable by `criterion`.
        '''
        return self.history[-1], value

