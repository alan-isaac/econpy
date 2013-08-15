'''
Unit tests for ls.py.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'

from itertools import izip
import random
import numpy as np
import numpy.linalg as la
import unittest

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.pytrix.pytrix import Vector, Vplus, dot, norm 
from econpy.pytrix.ls import rolsf, OLS


class testPytrix(unittest.TestCase):
	def test_ols(self):
		b0 = random.randint(1,10)
		b1 = random.randint(1,10)
		x = np.random.random((1000,1))
		e = np.random.random((1000,1)) * 0.1
		y = b0 + b1*x + e
		model = OLS(dep=y, indep=x)
		b1hat, b0hat = model.coefs #constant comes last
		self.assert_(abs(b1hat-b1)<0.1)
		self.assert_(abs(b0hat-b0)<0.1)

# +++++++++++++++++++++++++++++++++++++++++++
#                rolsftest.py
#    :author: j. c. hassler
#    12-feb-95
#    Originally written in Matlab.  Translated to Python 2-oct-07.
#      This is a simple driver program to test recursive OLS with a
#    forgetting factor, rolsf.  The process is an ARMA model driven by
#    a random input.  The parameters are estimated by ROLSF.
#
# ------------------------------------------

tht = [-.50, .25, 1., .25]    # true parameters
p = 1000.* np.eye(4)           # initialize covariance matrix
# large values because we have very low confidence in the initial guess.
th = [0., 0., 0., 0.]         # initial guesses at parameters
lam = 0.95                    # forgetting factor
xt = [0.,  0., 0., 0.]        # other initial values
x = [0., 0., 0., 0.]
a =  np.zeros(200,float)
b =  np.zeros(200,float)
indx =  np.zeros(200,int)
for i in range(200):
    if i>100:                 # change one of the parameters
        tht[0] = -.40         # .. on the fly.
# the point of the forgetting factor is to make the estimator responsive
# to such changes.
    e = 0.02*(.5 - random.random())  # random 'noise'
    u = 1.*(.5 - random.random())    # random forcing function
    yt =  np.inner(xt,tht)            # truth model
 
    xt[1] = xt[0]            # stuff in the new truth-value-y ...
    xt[0] = yt               # ... and new input
    xt[3] = xt[2]
    xt[2] = u
    y = yt + e               # add 'measurement noise' to the true value
    th,p = rolsf(x,y,p,th,lam)    # call recursive OLS with FF
    x[1] = x[0]              # stuff in the new y ...
    x[0] = y                 # ... and new input to the design model
    x[3] = x[2]
    x[2] = u
    a[i] = th[0]             # save for later plotting
    b[i] = th[1]
    indx[i] = i

'''
import matplotlib.pyplot as plt
plt.plot(indx,a,indx,b)
plt.grid()
plt.show()
'''

if __name__=="__main__":
	unittest.main()

