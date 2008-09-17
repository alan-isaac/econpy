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

import random, math
import types
import sys,os
import logging

have_numpy = False
try:
	import numpy as np
	from numpy import linalg
	have_numpy = True
except ImportError:
	logging.info("numpy not available")

# Polynomials in poly.py

# for IO see pytrix.IO






def gcd_euclid(r,n):
	'''Return greatest common divisor of r and n.

	:Parameters:
		- `r` : int
		- `n` : int

	:rtype:     integer
	:return:    the greatest common denominator
	            of the largest and smallest elements of `lst`
	:author:    Alan G. Isaac
	:since:     2004-10-28
	:contact:   mailto:aisaac AT american.edu
	:note:      uses only integer part of mn
	''' 
	n=int(max(abs( [r,n] )))
	r=int(min(abs( [r,n] )))
	while r!=0: (n,r)=(r,n%r)
	return n


def choice(x, axis=None):
	"""Select an element or subarray uniformly randomly.
	If axis is None, then a single element is chosen from the entire array.
	Otherwise, a subarray is chosen from the given axis.

	:author: Robert Kern
	:since: 20060220
	"""
	x = np.asarray(x)
	if axis is None:
		length = np.multiply.reduce(x.shape)
		n = random.randint(length)
		return x.flat[n]
	else:
		n = random.randint(x.shape[axis])
		# I'm sure there's a better way of doing this
		idx = map(slice, x.shape)
		idx[axis] = n
		return x[tuple(idx)]


def step_pts(x, y, use_numpy=True):
	'''Given x and y, return points for step function plot.

	:Parameters:
	 - `x`: [x0,x1,...,xn] list of x values (first coordinate)
	 - `y`: [y0,y1,...,yn] list of y values (second coordinate)
	:rtype: tuple of lists
	:return: (xnew,ynew)
		where xnew=(x0,x1,x1,...,xn,xn) and ynew=(y0,y0,y1,y1,...,yn).
	:since: 2005-05-15
	:date: 2007-09-27
	''' 
	nobs = len(x)
	assert nobs==len(y), "Inputs must be same length."
	if use_numpy and have_numpy:
		xnew = np.repeat(x,2)[1:]
		ynew = np.repeat(y,2)[:-1]
	else:
		xnew = [ x[(idx+1)//2] for idx in xrange(2*nobs-1) ]
		ynew = [ y[idx//2] for idx in xrange(2*nobs-1) ]
	return xnew, ynew



def cbrt(r, n=3):
	'''Cube root of real number.
	
	:Parameters:
	 - `r`: real number
	 - `n`: odd integer
	:rtype: float
	:note:
		Works for any odd integer `n` ::

			cbrt(r) = r^{1./n},      if r >= 0
			        = -(-r)^{1./n},  if r < 0

	:requires: `math` (Python module)
	:note: 0<r<1 => math.pow(r, n) = r^n for only r >= 0.
	:note: name is from libc (GNU C library)
	:see: http://www.gnu.org/software/libc/manual/html_node/Exponents-and-Logarithms.html
	:author: Alan G. Isaac
	:since: 2005-08-16
	'''
	assert n%2 and n==int(n) or r>=0, "n must be an odd integer if r<0"
	try: return r>=0 and math.pow(r,1./n) or -math.pow(-r,1./n)
	except: print "%s is not a real number"%(r)






def sinc(x):
	'''Sinus cardinalus. ::
	
		sinc(x) = sin(\pi x) / (\pi x),  if x != 0
		        = 1,                     if x = 0

	:param `x`: real number
	:rtype: float
	:note: The sinc() function usually comes up when doing Fourier Transform,
	       since sinc(f) is the fourier transform of 
	       ``rect(t) = {1, if |t| &lt; 1/2; 0, if |t| > 1/2}``
	:warning: Attend to the definition.
	          Contrast with http://en.wikipedia.org/wiki/Sinc_function
	:author: William Park
	'''
	from math import pi, sin
	try:
		x = pi * x
		return sin(x) / x
	except ZeroDivisionError:	# sinc(0) = 1
		return 1.0

#Vectors and Points

class vector(object):
	'''Simple vector class.
	
	:note: slice returns vector
	:note: returns vector instead of list from arithmetic operations
	:todo: switch dot and norm to generators (req. Python 2.4+)
	:author: Alan G. Isaac
	:since: 2005-08-19
	'''
	def __init__(self,seq,**kwds):
		self.data = list(seq)  #forces copy of data!
		self.length = len(self.data)
		if 'length' in kwds:
			assert(self.length==kwds['length']),"Data length does not match provided length"
		#result_class is for overriding result class in subclasses
		self.result_class = vector
		#core_attr: attributes to check conformability (see require_samecore)
		self.core_attr = dict(length=self.length)
	def __str__(self):
		return str(self.data)
	def __repr__(self):
		return "vector: "+repr(self.data)
	def __len__(self):
		return len(self.data)
	def __getitem__(self, item):  #http://www.python.org/doc/2.3.4/whatsnew/section-slices.html
		if isinstance(item, slice):
			indices = item.indices(len(self.data))
			return self.result_class([self.data[i] for i in range(*indices)])
		else:
			return self.data[i]
	def __setitem__(self,i,xi):
		self.data[i] = xi
	def __iter__(self):
		return iter(self.data)
	def __add__(self,other):
		self.require_samecore(other)
		return self.result_class([xi+yi for (xi,yi) in zip(self,other)],**self.core_attr)
	def __sub__(self,other):
		self.require_samecore(other)
		return self.result_class([xi-yi for (xi,yi) in zip(self,other)],**self.core_attr)
	def __neg__(self):
		return self.result_class([-xi for xi in self],**self.core_attr)
	def __abs__(self):
		return self.result_class([abs(xi) for xi in self],**self.core_attr)
	def __rmul__(self,scalar): #scalar multiplication
		assert(isinstance(scalar,(int,float,complex))), "scalar multiplication needs number"
		return self.result_class([scalar*xi for xi in self.data],**self.core_attr)
	def __eq__(self,other):
		try:
			self.require_samecore(other)
			return self.data==other.data
		except:
			return False
	def require_samecore(self,other):
		missing = []
		for attr in self.core_attr:
			try:
				if self.core_attr[attr]!=other.core_attr[attr]:
					raise ValueError('Operands have different '+str(attr))
			except:
				missing.append(attr)
		if missing:
			raise TypeError('Operand missing core attributes: '+str(missing))
	def as_column(self):
		'''Returns vector as 2-dimensional column vector.
		'''
		return [[datum] for datum in self]
	def dot(self,other):
		"""Simple vector dot (inner) product. ::

			dot(x, y) = \sum_i x_i y_i

		:param `y`: list of floats
		:note: inputs can be any iterables of numbers
		:see: http://en.wikipedia.org/wiki/Dot_product
		"""
		assert(len(self)==len(other))
		return sum([xi*yi for xi,yi in zip(self,other)])
	def norm(self,p=2,normtype=None):
		"""Vector norm. ::

					||x||1 = \sum_i |x_i|
					||x||2 = \sqrt{\sum_i x_i^2}
					||x||infty = \max |x_i|

		:Parameters:
			`p`: float
				the normtype: ``||x||p = (\sum_i |x_i|^p)^(1/p)``
			`normtype`: string
				the normtype: 'taxi' (p=1) or 'euclid' (p=2) or 'max' (p=infty)
		:see: http://en.wikipedia.org/wiki/Vector_norm
		"""
		if normtype:
			normdict = {'taxi':1,'euclid':2,'max':'infty','infty':'infty'}
			try: p = normdict[normtype]
			except: raise ValueError, 'unknown norm type'
		if p == 1:            # ||x||1
			return sum([abs(xi) for xi in self.data])
		elif p == 2:	      # ||x||2 (the default)
			return math.sqrt(sum([xi*xi for xi in self.data]))
		elif p == 'infty':    # ||x||oo
			return max([abs(xi) for xi in self.data])
		else:
			try: return math.pow(sum([abs(xi)**p for xi in self.data]),1./p)
			except: raise ValueError, 'unknown norm type'
		
class vplus(vector):
	'''Augments the vector class to include element-by-element operations.'''
	def __init__(self,seq,**kwds):
		self.data = list(seq)  #forces copy of data!
		self.length = len(self.data)
		if 'length' in kwds:
			assert(self.length==kwds['length']),"Data length does not match provided length"
		self.result_class = vplus
		self.core_attr = dict(length=self.length)
	def __repr__(self):
		return "vplus: "+repr(self.data)
	def __mul__(self,other):
		self.require_samecore(other)
		return self.result_class([xi*yi for (xi,yi) in zip(self.data,other)],**self.core_attr)
	def __div__(self,other):  #careful: not insisting on truediv
		self.require_samecore(other)
		return self.result_class([xi/yi for (xi,yi) in zip(self.data,other)],self.core_attr)
	def __pow__(self,expon):
		if isinstance(expon,(int,float)):
			self2expon  = self.result_class([xi**expon for xi in self.data])
		else:
			assert(len(self)==len(y)),"vectors must have same length"
			self2expon = self.result_class([xi**yi for (xi,yi) in zip(self,y)])
		return self2expon



class Pt2d(vector):
	def __init__(self,p,polar=False,in_degrees=False):
		if polar: #convert to rectangular coordinates
			self.data=circ2rect(p,in_degrees=in_degrees)
		else:
			self.data = p
	def __repr__(self):
		"pt2d(%s,%s)"%self.data
	def move(self,dp):
		'''Move point by dp=(dx,dy)'''
		self.data=self+dp
	def __str__(self):
		"(%s,%s)"%self.data

def circ2rect2d(rw, in_degrees=False):
	"""Convert 2-D coordinates from polar (r,w) to rectangular (x,y).

	:Parameters:
		`rw`: (float,float)
			radius length,
			angle in radians (default) or degrees
		`in_degrees`: bool
			flag `w` as in radians or degrees
	:rtype: (float,float)
	:return: (x,y), the real abscissa and ordinate in ``R^2``
	:see: http://en.wikipedia.org/wiki/Angle
	:see: http://en.wikipedia.org/wiki/Coordinates_%28mathematics%29
	:contact: alan DOT isaac AT gmail DOT com
	"""
	(r,w)=rw
	if in_degrees:
		w = math.radians(w) #transform degrees to radians
	return r*math.cos(w), r*math.sin(w)

def rect2circ2d(xy, in_degrees=False):
	"""Convert 2-D point from rectangular (x,y) to polar (r,w).

	:Parameters:
		`xy`: (float,float)
			abscissa (`x`), ordinate (`y`) in ``R^2``
		`in_degrees`: bool
			flag `w` as in radians or degrees
	:rtype: (float,float)
	:return: (r,w),
		the radius length (r)
		and angle (w) in radians (default) or degrees
	:see: http://en.wikipedia.org/wiki/Angle
	:see: http://www.python.org/doc/current/lib/module-math.html#hypot
	:see: http://www.python.org/doc/current/lib/module-math.html#atan2
	:see: http://en.wikipedia.org/wiki/Coordinates_%28mathematics%29
	:note: atan2(y/x) always in [-\pi,\pi] radians (i.e., [-180,180] degrees)
	:contact: alan DOT isaac AT gmail DOT com
	"""
	(x,y) = xy
	w = in_degrees and 180.0*math.atan2(y,x)/math.pi or math.atan2(y,x)
	return math.hypot(x,y), w

def nearest2d(pt,ptlst,polar=False,in_degrees=False):
	"""Find 2-D point in `ptlst` nearest to `pt`.

	:Parameters:
		`pt`: (number,number)
			a point
		`ptlst`: list
			list of points (2-tuples), possible neighbors
		`polar`: bool
			False (default) if pt,ptlst have rectangular coordinates,
			True if pt,ptlst in polar coordinates
		`in_degrees`: bool
			flag polar coordinates as in radians or degrees
	:rtype: 2-tuple of floats
	:return: (x,y), the real abscissa and ordinate in ``R^2``
	:requires: `rect2circ` and `circ2rect`
	:see: http://en.wikipedia.org/wiki/Angle
	:see: http://mail.python.org/pipermail/python-list/2003-November/192870.html
	:see: http://mail.python.org/pipermail/python-list/2003-November/193046.html
	:contact: alan DOT isaac AT gmail DOT com
	"""
	if polar:
		pt = circ2rect(pt,in_degrees=in_degrees)
		ptlst = [circ2rect(ptlsti,in_degrees=in_degrees) for ptlsti in ptlst]
	cpt=complex(*pt) #represent 2D pt as complex number
	dist,nearest = min([(abs(cpt-complex(*ptlsti)),ptlsti) for ptlsti in ptlst])
	return polar and rect2circ(nearest,in_degrees=in_degrees) or nearest


class kdtree:
	'''kd-tree class with nearest neighbor detection for new points.

	:see: http://mail.python.org/pipermail/python-list/2003-November/192870.html
	:see: http://en.wikipedia.org/wiki/Kd-tree
	:since: Mon Nov 3 20:11:45 EST 2003
	:author: David Eppstein
	:contact: eppstein at ics.uci.edu
	'''
	def __init__(self,dim=2,index=0):
		self.dim = dim
		self.index = index
		self.split = None
	def dist2(p,q):
		"""Squared distance between p and q."""
		d = 0
		for i in range(len(p)):
			d += (p[i]-q[i])**2
		return d
	dist2 = staticmethod(dist2)
	def addPoint(self,p):
		"""Include another point in the kD-tree."""
		if self.split is None:
			self.split = p
			self.left = kdtree(self.dim, (self.index + 1) % self.dim)
			self.right = kdtree(self.dim, (self.index + 1) % self.dim)
		elif self.split[self.index] < p[self.index]:
			self.left.addPoint(p)
		else:
			self.right.addPoint(p)
	def nearestNeighbor(self,q,maxdist2):
		"""Find pair (d,p) where p is nearest neighbor and d is squared
		distance to p. Returned distance must be within maxdist2; if
		not, no point itself is returned.
		"""
		solution = (maxdist2+1,None)
		if self.split is not None:
			solution = min(solution, (kdtree.dist2(self.split,q),self.split))
			d2split = (self.split[self.index] - q[self.index])**2
			if self.split[self.index] < p[self.index]:
				solution = min(solution,
					self.left.nearestNeighbor(q,solution[0]))
				if d2split < solution[0]:
					solution = min(solution,
						self.right.nearestNeighbor(q,solution[0]))
			else:
				solution = min(solution,
					self.right.nearestNeighbor(q,solution[0]))
				if d2split < solution[0]:
					solution = min(solution,
						self.left.nearestNeighbor(q,solution[0]))
		return solution
    



# Zeros of Functions

def newton(func, funcd, x, TOL=1e-6):	# f(x)=func(x), f'(x)=funcd(x)
	"""Solve for a zero of function using Newton-Raphson method.


	:note: real = func(real) 
	:note: real = funcd(real) 
	:note: real = newton(func, funcd, real [, TOL=real])

	Ubiquitous Newton-Raphson algorithm for solving ::
	
		f(x) = 0

	where a root is repeatedly estimated by ::
	
		x = x - f(x)/f'(x)

	until ``|dx|/(1+|x|) < TOL`` is achieved.  This termination condition is a
	compromise between ::

		|dx| < TOL,  if x is small
		|dx|/|x| < TOL,  if x is large

	Even though it converges quadratically once a root has
	been "sighted", it does not guarantee global convergence.  So, I use
	print statement to see intermediate results.  
	:author: William Park
	"""
	f, fd = func(x), funcd(x)
	count = 0
	while 1:
		dx = f / float(fd)
		if abs(dx) < TOL * (1 + abs(x)): return x - dx
		x = x - dx
		f, fd = func(x), funcd(x)
		count = count + 1
	print "newton(%d): x=%s, f(x)=%s" % (count, x, f)



def secant(func, oldx, x, TOL=1e-6):	# f(x)=func(x)
	"""Solve for a zero of function using Secant method. ::

		real = func(real) 
		real = secant(func, real, real [, TOL=real])



	:note:
		Similar to Newton's method, but the derivative is estimated by divided
		difference using only function calls.  A root is estimated by:
		
			x = x - f(x) (x - oldx)/(f(x) - f(oldx))
			
		where oldx = x[i-1] and x = x[i].

	:note: This routine is used when f'() is difficult or impossible
		to evaluate.  It requires 2 initial points to start the iteration, and
		the order of convergence is 1.6, which is better than linear method
		like bisection but not as fast as quadratic method like Newton.  
	:author: William Park
	"""
	oldf, f = func(oldx), func(x)
	if (abs(f) > abs(oldf)):		# swap so that f(x) is closer to 0
		oldx, x = x, oldx
		oldf, f = f, oldf
	count = 0
	while 1:
		dx = f * (x - oldx) / float(f - oldf)
		if abs(dx) < TOL * (1 + abs(x)): return x - dx
		oldx, x = x, x - dx
		oldf, f = f, func(x)
		count = count + 1
	print "secant(%d): x=%s, f(x)=%s" % (count, x, f)


# Integration



def closedpoints(func, a, b, TOL=1e-6):		# f(x)=func(x)
	"""Closed integration of function using extended Simpson's rule. ::

		real = func(real) 
		real = closedpoints(func, real, real [, TOL=real])



	Closed Simpson's rule for ``\int_a^b f(x) dx``:
	Divide [a,b] iteratively into h, h/2, h/4, h/8, ... step sizes; and,
	for each step size, evaluate f(x) at a+h, a+3h, a+5h, a+7h, ..., b-3h,
	b-h, noting that other points have already been sampled.

	At each iteration step, data are sampled only where necessary so that
	the total data is represented by adding sampled points from all
	previous steps::

		step 1:	h	a---------------b
		step 2:	h/2 	a-------^-------b
		step 3:	h/4	a---^-------^---b
		step 4:	h/8	a-^---^---^---^-b
		total:		a-^-^-^-^-^-^-^-b

	So, for step size of h/n, there are n intervals, and the data are
	sampled at the boundaries including the 2 end points.

	If old = Trapezoid formula for an old step size 2h, then Trapezoid
	formula for the new step size h is obtained by ::

		new = old/2 + h{f(a+h) + f(a+3h) + f(a+5h) + f(a+7h) +...+ f(b-3h) + f(b-h)}

	Also, Simpson formula for the new step size h is given by
	``simpson = (4 new - old)/3``
	:author: William Park
	"""
	h = b - a
	old2 = old = h * (func(a) + func(b)) / 2.0
	count = 0
	while 1:
		h = h / 2.0
		x, sum = a + h, 0
		while x < b:
			 sum = sum + func(x)
			 x = x + 2 * h
		new = old / 2.0 + h * sum
		new2 = (4 * new - old) / 3.0
		if abs(new2 - old2) < TOL * (1 + abs(old2)): return new2
		old = new	# Trapezoid
		old2 = new2	# Simpson
		count = count + 1
	print 'closedpoints(%d): Trapezoid=%s, Simpson=%s' % (count, new, new2)

def openpoints(func, a, b, TOL=1e-6):		# f(x)=func(x)
	"""Open integration of function using extended Simpson's rule. ::

		real = func(real) 
		real = openpoints(func, real, real [, TOL=real])

	Open Simpson's rule (excluding end points) for ``\int_a^b f(x) dx``
	Divide ``[a,b]`` iteratively into ``h, h/3, h/9, h/27, ...`` step sizes; and,
	for each step size, evaluate f(x) at
	``a+h/2, a+2h+h/2, a+3h+h/2, a+5h+h/2, a+6h+h/2, ... , b-3h-h/2, b-2h-h/2, b-h/2``,
	noting that other points have already been sampled.

	At each iteration step, data are sampled only where necessary so that
	the total data is represented by adding sampled points from all
	previous steps::
	
		step 1:	h	a-----------------^-----------------b
		step 2:	h/3	a-----^-----------------------^-----b
		step 3:	h/9	a-^-------^---^-------^---^-------^-b
		total:		a-^---^---^---^---^---^---^---^---^-b

	So, for step size of h/n, there are n intervals, and the data are
	sampled at the midpoints.

	If old = Trapezoid formula for an old step size 3h, then Trapezoid
	formula for the new step size h is obtained by ::
	
		new = old/3 + h{f(a+h/2) + f(a+2h+h/2) + f(a+3h+h/2) + f(a+5h+h/2)
		+ f(a+6h+h/2) +...+ f(b-3h-h/2) + f(b-2h-h/2) + f(b-h/2)}

	Also, Simpson formula for the new step size h is given by::
	
		simpson = (9 new - old)/8

	Both closedpoints() and openpoints() routines use
	Trapezoid formula to calculate Simpson's formula, as opposed to more
	direct summation.  And, because the discrete integration is over
	uniformly sampled points, it can take advantage of already sampled
	data taken at previous iterations.  
	:author: William Park
	"""
	h = b - a
	old2 = old = h * func((a + b) / 2.0)
	count = 0
	while 1:
		h = h / 3.0
		x, sum = a + 0.5 * h, 0
		while x < b:
			 sum = sum + func(x) + func(x + 2 * h)
			 x = x + 3 * h
		new = old / 3.0 + h * sum
		new2 = (9 * new - old) / 8.0
		if abs(new2 - old2) < TOL * (1 + abs(old2)): return new2
		old = new	# Trapezoid
		old2 = new2	# Simpson
		count = count + 1
	print 'openpoints(%d): Trapezoid=%s, Simpson=%s' % (count, new, new2)


# FFT

def nextpow2(i):
	"""Find 2^n that is equal to or greater than

	This is an internal function used by fft(), because the FFT
	routine requires that the data size be a power of 2.  
	:author: William Park
	"""
	n = 2
	while n < i: n = n * 2
	return n



def bitrev(x):
	"""Return bit-reversed array for FFT. ::

		list = bitrev(list)

	Return bit-reversed list, whose length is assumed to be 2^n:
	eg. 0111  1110 for N=2^4.
	:author: William Park
	"""
	N, x = len(x), x[:]
	if N != nextpow2(N): raise ValueError, 'N is not power of 2'
	for i in range(N):
	 	k, b, a = 0, N>>1, 1
	 	while b >= a:
	 	    if b & i: k = k | a
		if a & i: k = k | b
		b, a = b>>1, a<<1
	if i < k:		# important not to swap back
		 x[i], x[k] = x[k], x[i]
	return x


def fft(x, sign=-1):
	"""FFT for 2^n data size [5] ::

		list = fft(list [, sign=1]) 

	:author: William Park
	:see: `ifft` for inverse Fast Fourier Transform
	:note: FFT using Cooley-Tukey algorithm where N = 2^n.  The choice of
		e^{-j2\pi/N} or e^{j2\pi/N} is made by 'sign=-1' or 'sign=1'
		respectively.  Since I prefer Engineering convention, I chose
		'sign=-1' as the default.
	:note: FFT is performed as follows:

	 1. bit-reverse the array.
	 2. partition the data into group of m = 2, 4, 8, ..., N data points.
	 3. for each group with m data points,
		1. divide into upper half (section A) and lower half (section B),
		each containing m/2 data points.
		2. divide unit circle by m.
		3. apply "butterfly" operation::
		
			|a| = |1  w||a|	or	a, b = a+w*b, a-w*b
			|b|   |1 -w||b|

		where a and b are data points of section A and B starting from
		the top of each section, and w is data points along the unit
		circle starting from z = 1+0j.
	 4. FFT ends after applying "butterfly" operation on the entire data array as whole, when m = N.
	"""
	from cmath import pi, exp
	N, W = len(x), []
	for i in range(N):		# exp(-j...) is default
		W.append(exp(sign * 2j * pi * i / N))
	x = bitrev(x)
	m = 2
	while m <= N:
		for s in range(0, N, m):
			for i in range(m/2):
				n = i * N / m
				a, b = s + i, s + i + m/2
				x[a], x[b] = x[a] + W[n % N] * x[b], x[a] - W[n % N] * x[b]
			m = m * 2
	return x

def ifft(X):
	"""Inverse FFT for 2^n data size [5] ::

		list = ifft(list)

	Inverse FFT with normalization by N, so that x == ifft(fft(x)) within
	round-off errors.

	I calculate N points along the unit circle at the
	beginning instead of calculating as needed; so, this should be more
	efficient than the FFT routine given in Numerical Recipes in
	C, but not by much.  

	:type `X`: list
	:rtype: list
	:see: `fft` for Fast Fourier Transform
	:author: William Park
	"""
	N, x = len(X), fft(X, sign=1)	# e^{j2\pi/N}
	for i in range(N):
		x[i] = x[i] / float(N)
	return x



def dft(x, sign=-1): 
	"""DFT using direct summation. ::

		list = dft(list [, sign=1]) 
		X(n) = \sum_k W^{nk} x(k),  W = e^{-j2\pi/N}

	where N need not be power of 2.  The choice of e^{-j2\pi/N} or
	e^{j2\pi/N} is made by "sign=-1" or "sign=1" respectively.
	:see: `idft` for inverse
	:author: William Park
	"""
	from cmath import pi, exp
	N, W = len(x), []
	for i in range(N):		# exp(-j...) is default
		W.append(exp(sign * 2j * pi * i / N))
	X = []
	for n in range(N):
		sum = 0
		for k in range(N):
			 sum = sum + W[n * k % N] * x[k]
		X.append(sum)
	return X

def idft(X):
	"""inverse DFT using direct summation ::

		list = idft(list)

	Inverse DFT with normalization by N, so that x == idft(dft(x)) within
	round-off errors.

	I wrote these functions to test FFT routines.  DFT should
	only be used for small data size (less than 64).  
	:author: William Park
	"""
	N, x = len(X), dft(X, sign=1)	# e^{j2\pi/N}
	for i in range(N):
		x[i] = x[i] / float(N)
	return x



# Convolution and Correlation


def conv(x, y):
	"""Discrete convolution [5] ::

		list = conv(list, list) 

	Convolution of 2 casual signals,
	``x(t<0) = y(t<0) = 0``,
	using discrete summation. ::

		x*y(t) = \int_{u=0}^t x(u) y(t-u) du = y*x(t)

	where the size of x[], y[], x*y[] are P, Q, N=P+Q-1 respectively.
	:see: `corr` for correlation
	:author: William Park
	"""
	P, Q, N = len(x), len(y), len(x)+len(y)-1
	z = []
	for k in range(N):
		t, lower, upper = 0, max(0, k-(Q-1)), min(P-1, k)
	for i in range(lower, upper+1):
		 t = t + x[i] * y[k-i]
	z.append(t)
	return z

def corr(x, y):
	"""Discrete correlation [5]
	Correlation of 2 casual signals, x(t<0) = y(t<0) = 0, using discrete
	summation::

		Rxy(t) = \int_{u=0}^{\infty} x(u) y(t+u) du = Ryx(-t)

	where the size of x[], y[], Rxy[] are P, Q, N=P+Q-1 respectively.

	The Rxy[i] data is not shifted, so relationship with the continuous
	Rxy(t) is preserved.  For example, Rxy(0) = Rxy[0], Rxy(t) = Rxy[i],
	and Rxy(-t) = Rxy[-i].  The data are ordered as follows::
	
		t:	-(P-1),  -(P-2),  ..., -3,  -2,  -1,  0, 1, 2, 3, ..., Q-2, Q-1
		i:	N-(P-1), N-(P-2), ..., N-3, N-2, N-1, 0, 1, 2, 3, ..., Q-2, Q-1

	:see: `conv` for convolution
	:author: William Park
	"""
	P, Q, N = len(x), len(y), len(x)+len(y)-1
	z1=[]
	for k in range(Q):
		t, lower, upper = 0, 0, min(P-1, Q-1-k)
	for i in range(lower, upper+1):
		 t = t + x[i] * y[i+k]
	z1.append(t)		# 0, 1, 2, ..., Q-1
	z2=[]
	for k in range(1,P):
		t, lower, upper = 0, k, min(P-1, Q-1+k)
	for i in range(lower, upper+1):
		 t = t + x[i] * y[i-k]
	z2.append(t)		# N-1, N-2, ..., N-(P-2), N-(P-1)
	z2.reverse()
	return z1 + z2

def fftconv(x, y):
	"""FFT convolution [5] ::

		list = fftconv(list, list) 

	FFT convolution using relation ``x*y  XY``
	where x and y have been zero-padded to length N,
	such that N >= P+Q-1 and N = 2^n.
	:see: `fftcorr` for FFT correlation
	:author: William Park
	"""
	N, X, Y, x_y = len(x), fft(x), fft(y), []
	for i in range(N):
		x_y.append(X[i] * Y[i])
	return ifft(x_y)



def fftcorr(x, y):
	"""FFT correlation [5] ::

		list = fftcorr(list, list)

	FFT correlation using relation ``Rxy  X'Y``
	where x and y have been zero-padded to length N, such that N >=
	P+Q-1 and N = 2^n.

	Due to the nature of FFT routines, fftconv() and fftcorr()
	assume that input data have been zero-padded to a length that is big
	enough to hold the output size P+Q-1.  However, conv() and corr() can
	accept any length, because they use direction summation.  

	:see: `fftconv` for FFT convolution
	:author: William Park
	"""
	N, X, Y, Rxy = len(x), fft(x), fft(y), []
	for i in range(N):
		Rxy.append(X[i].conjugate() * Y[i])
	return ifft(Rxy)




# Statistics
# see tseries.py

def meanstdv(x):
	"""Mean and standard deviation of data. ::

		real, real = meanstdv(list)

	Calculate mean and standard deviation of data x[]::
	
		 mean = {\sum_i x_i \over n}
		 std = sqrt(\sum_i (x_i - mean)^2 \over n-1)

	:author: William Park
	"""
	from math import sqrt
	n, mean, std = len(x), 0, 0
	for a in x:
		mean = mean + a
	mean = mean / float(n)
	for a in x:
		std = std + (a - mean)**2
	std = sqrt(std / float(n-1))
	return mean, std





#----------------------------------------------------------------------#
#  function:	testLR                                                  #
#----------------------------------------------------------------------#
# Author:	   Chris Rathman, 25 July 2000
# http://www.angelfire.com/tx4/cus/regress/python.html
# File:	     pytrix.py
# Purpose:	  Simple linear and multivariate regression functions
# Version:	  1.00
def testLR():
	# Purpose: try out some simple regression tests

	# first order equation: Y = 1 + 2X
	myCoefficients = linearRegression([[1, 0], [3, 1], [5, 2]], 1)
	print myCoefficients

	# get the r-squared value for the regression
	myRSquared = linearRSquared([[1, 0], [3, 1], [5, 2]], myCoefficients)

	# first order equation: Y = 2 + 2X
	print linearRegression([[1, 0], [3, 1], [3, 0], [5, 1]], 1)

	# first order equation: Y = 100 + 50X
	myData = []
	for x in range(100):
	   myData.append([100 + x*50, x])
	print linearRegression(myData, 1)

	# second order equation: Y = 1 + 2X + 3X^2
	myData = []
	for x in range(100):
	   myData.append([1 + 2*x + 3*x*x, x])
	print linearRegression(myData, 2)

	# third order equation: Y = 4 + 3X + 2X^2 + 1X^3
	myData = []
	for x in range(100):
	   myData.append([4 + 3*x + 2*x*x + 1*x*x*x, x])
	print linearRegression(myData, 3)

	# multivariate equation: Y = 6 + 5X + 4X^2 + 3XZ + 2Z + 1Z^2
	myData = []
	for x in range(100):
	   z = random.randint(0, 100)
	   myData.append([6 + 5*x + 4*x*x + 3*x*z + 2*z + 1*z*z, x, z])
	myEquations = []
	myEquations.append(lambda rawItem, coefIndex: 1)
	myEquations.append(lambda rawItem, coefIndex: rawItem[1])
	myEquations.append(lambda rawItem, coefIndex: rawItem[1] * rawItem[1])
	myEquations.append(lambda rawItem, coefIndex: rawItem[1] * rawItem[2])
	myEquations.append(lambda rawItem, coefIndex: rawItem[2])
	myEquations.append(lambda rawItem, coefIndex: rawItem[2] * rawItem[2])
	print regression(myData, myEquations)


#----------------------------------------------------------------------#
#  function:	linearRegression                                        #
#----------------------------------------------------------------------#
# Author:	   Chris Rathman, 25 July 2000
# http://www.angelfire.com/tx4/cus/regress/python.html
# File:	     pyTrix.py
# Purpose:	  Simple linear and multivariate regression functions
# Version:	  1.00

def linearRegression(rawData, equationOrder):

	# Purpose: Regress the coefficients for an equation of the form:
	#     Y = C0 + C1*X + C2*X^2 + ... + Cn*X^n
	# The regression outputs a list of the coefficients ([C0,C1,..,C[n])

	# rawData: A supplied list of Y and X values which serve as a basis
	# for computing the coefficients.  The general form of the list is:
	# [[Y0, X0],[Y1, X1],...,[Ym,Xm]].

	# equationOrder: The equation order is the power function for the X
	# variable where the number of coefficients returned is the equation + 1.
	# For example, an equation of 1 maps to Y = C0 + C1X.  An equation order
	# of 2 maps to Y = C0 + C1*X + C2*X*X.

	# require part of contract
	assert(type(rawData) == types.ListType), \
	   "Raw data input must be a list"
	assert(equationOrder > 0), \
	   "Equation order must be greater than 0th order"
	assert(len(rawData) >= equationOrder), \
	   "Number of data points must be >= to number of coefficients be calculated"
	for each in (rawData):
	   assert(type(each) == types.ListType), \
	      "Raw data input must be a list of data values"
	   assert(len(each) > 1), \
	      "More than one data point is required for the raw data"
	   assert(len(each) == len(rawData[0])), \
	      "All data points in raw data must have the same number items"

	xEquationForm = [lambda rawItem, coefIndex: pow(rawItem[1], coefIndex)]
	return regression(rawData, xEquationForm * (equationOrder+1))

#----------------------------------------------------------------------#
#  function:	regression                                              #
#----------------------------------------------------------------------#
def regression(rawData, xEquationForm, yEquationForm = lambda rawItem: rawItem[0]):

	# Purpose: Regress the coefficients for an equation of a generalized form
	# as supplied by the xEquationForm and yEquationForm functions:
	#     Y = C0*X0 + C1*X1 + C2*X2 + ... + Cn*Xn
	# Where Y = yEquationForm() and Xn = xEquationForm[n]()
	# The regression outputs a list of the coefficients ([C0,C1,..,C[n])

	# rawData: A supplied list of Y and X values which serve as a basis
	# for computing the coefficients.  The general form of the list is:
	# [[Y0, X0],[Y1, X1],...,[Ym,Xm]].

	# equationOrder: The equation order is the power function for the X
	# variable where the number of coefficients returned is the equation + 1.
	# For example, an equation of 1 maps to Y = C0 + C1X.  An equation order
	# of 2 maps to Y = C0 + C1*X + C2*X*X.

	# require part of contract
	assert(type(rawData) == types.ListType), \
	   "Raw data input must be a list"
	assert(type(xEquationForm) == types.ListType), \
	   "X Equation form must be defined in a list"
	assert(type(yEquationForm == types.FunctionType)), \
	   "Y Equation form must be a lambda function"
	assert(len(xEquationForm) > 0), \
	   "X Equation form must not be an empty list"
	assert(len(rawData) >= len(xEquationForm)), \
	   "Number of data points must be >= to number of coefficients be calculated"
	for each in (xEquationForm):
	   assert(type(each) == types.FunctionType), \
	      "X Equation form must be lambda functions"
	for each in (rawData):
	   assert(type(each) == types.ListType), \
	      "Raw data input must be a list of data values"
	   assert(len(each) > 1), \
	      "More than one data point is required for the raw data"
	   assert(len(each) == len(rawData[0])), \
	      "All data points in raw data must have the same number items"

	# number of coefficients being solved for
	numCoefficients = len(xEquationForm)

	# the value of each term for the equation
	term = [0] * numCoefficients

	# the matrices for the simultaneous equations
	B = [0] * numCoefficients
	A = []
	for i in range(numCoefficients):
	   A.append([0] * numCoefficients)

	# loop through all the raw data samples
	for each in rawData:

	   # sum the y values
	   yCurrent = float(yEquationForm(each))
	   B[0] = B[0] + yCurrent

	   # sum the x values
	   for i in range(numCoefficients):
	      term[i] = float(xEquationForm[i](each, i))
	      A[0][i] = A[0][i] + term[i]

	   # now set up the rest of rows in the matrices
	   # (multiplying each row by each term)
	   for i in range(1, numCoefficients):
	      B[i] = B[i] + yCurrent * term[i]
	      for j in range(numCoefficients):
	         A[i][j] = A[i][j] + term[i] * term[j]

	# solve for the coefficients
	return gauss(A, B)

#----------------------------------------------------------------------#
#  function:	linearRSquared                                          #
#----------------------------------------------------------------------#
def linearRSquared(rawData, coefficients):

	# Purpose: Compute the R-Squared statistic for the supplied coefficients

	# require part of contract
	assert(type(rawData) == types.ListType), \
	   "Raw data input must be a list"
	assert(type(coefficients) == types.ListType), \
	   "Computed coefficients must be a list"
	assert(len(coefficients) > 0), \
	   "At least coefficient is required"
	assert(len(rawData) >= len(coefficients)), \
	   "Number of data points must be >= to number of coefficients"
	for each in (rawData):
	   assert(type(each) == types.ListType), \
	      "Raw data input must be a list of data values"
	   assert(len(each) > 1), \
	      "More than one data point is required for the raw data"
	   assert(len(each) == len(rawData[0])), \
	      "All data points in raw data must have the same number items"

	xEquationForm = [lambda rawItem, coefIndex: pow(rawItem[1], coefIndex)]
	return solveRSquared(rawData, coefficients, xEquationForm * len(coefficients))

#----------------------------------------------------------------------#
#  function: solveRSquared	                                          #
#----------------------------------------------------------------------#
def solveRSquared(rawData, coefficients, xEquationForm, \
	yEquationForm = lambda rawItem: rawItem[0]):

	# Purpose: Compute the R-Squared statistic for the supplied coefficients

	# require part of contract
	assert(type(rawData) == types.ListType), \
	   "Raw data input must be a list"
	assert(type(xEquationForm) == types.ListType), \
	   "X Equation form must be defined in a list"
	assert(type(yEquationForm == types.FunctionType)), \
	   "Y Equation form must be a lambda function"
	assert(len(xEquationForm) > 0), \
	   "X Equation form must not be an empty list"
	assert(len(rawData) >= len(xEquationForm)), \
	   "Number of data points must be >= to number of coefficients be calculated"
	for each in (xEquationForm):
	   assert(type(each) == types.FunctionType), \
	      "X Equation form must be lambda functions"
	for each in (rawData):
	   assert(len(each) == len(rawData[0])), \
	      "All data points in raw data must have the same number items"
	   assert(len(each) > 1), \
	      "More than one data point is required for the raw data"

	# number of coefficients being solved for
	numCoefficients = len(xEquationForm)

	# sum of y*y
	ysquare = 0

	# number of raw data samples
	samples = len(rawData)

	# the value of each term for the equation
	term = [0] * numCoefficients

	# the matrices for the simultaneous equations
	B = [0] * numCoefficients
	A = []
	for i in range(numCoefficients):
	   A.append([0] * numCoefficients)

	# use the first column as the default value for the dependent variable
	if yEquationForm == []:
	   yEquationForm = lambda rawItem: rawItem[0]

	# loop through all the raw data samples
	for each in rawData:

	   # sum the y values
	   yCurrent = float(yEquationForm(each))
	   B[0] = B[0] + yCurrent
	   ysquare = ysquare + yCurrent * yCurrent

	   # sum the x values
	   for i in range(numCoefficients):
	      term[i] = float(xEquationForm[i](each, i))
	      A[0][i] = A[0][i] + term[i]

	   # now set up the rest of rows in the matrices
	   # (multiplying each row by each term)
	   for i in range(1, numCoefficients):
	      B[i] = B[i] + float(yCurrent * term[i])
	      for j in range(numCoefficients):
	         A[i][j] = A[i][j] + term[i] * term[j]

	# calculate the r-squared statistic
	sumsquare = 0
	yaverage = B[0] / samples
	for i in range(numCoefficients):
	   xaverage = A[0][i] / samples
	   sumsquare = sumsquare + coefficients[i] * (B[i] - (samples * xaverage * yaverage))
	return sumsquare / (ysquare - (samples * yaverage * yaverage))

def gauss(AMatrix, BMatrix):
	'''Solve linear equations of the form ::

	      |A00 A01 ... A0n|   |coefficient0|   |B0|
	      |A10 A11 ... A1n| * |coefficient1| = |B1|
	      |... ... ... ...|   |     ...    |   |..|
	      |An0 An1 ... Ann|   |coefficientn|   |Bn|
	
	where ``|A|`` and ``|B|`` are supplied and ``|coefficient|`` is the solution.
	:author: William Park
	'''

	# require part of contract
	assert(type(AMatrix) == types.ListType), \
	  "Input matrix must be a list"
	assert(type(BMatrix) == types.ListType), \
	  "Input matrix must be a list"
	assert(len(AMatrix) > 0), \
	  "Input matrix must not be an empty list"
	assert(len(AMatrix) == len(BMatrix)), \
	  "A and B matrix must have same number of rows"
	for each in (AMatrix):
	  assert(len(each) == len(AMatrix)), \
		 "A matrix must be of square (NxN) dimensions"

	# get the length of the matrix
	n = len(AMatrix)

	# copy the matrices to local variables - inplace substitution used
	A = map(lambda x: list(x), AMatrix)
	B = list(BMatrix)

	# initialize the output results
	coefficients = [0] * n

	# condition the matrix for the solution
	for i in range(n-1):
	  pivot = A[i][i]
	  assert(pivot != 0), \
		 "Zero pivot value encountered"
	  for j in range(i+1, n):
		 multiplier = float(A[j][i]) / pivot
		 for k in range(i+1, n):
			A[j][k] = A[j][k] - multiplier * A[i][k]
		 B[j] = B[j] - multiplier * B[i]

	# solve for the coefficients
	assert(A[n-1][n-1] != 0), \
	  "Divide by zero encountered in solution"
	coefficients[n-1] = float(B[n-1]) / A[n-1][n-1]
	for i in range(n-2, -1, -1):
	  top = B[i]
	  for j in range(i+1, n):
		 top = top - (A[i][j]* coefficients[j])
	  assert(A[i][i] != 0), \
		 "Divide by zero encountered in solution"
	  coefficients[i] = float(top) / A[i][i]

	return coefficients



class interp2:
	""" Class for interpolating values

	- coded just like the octave algorithm for this problem.
	- this is nasty code !!!
	- it just does, what I needed

	:date: 2004-10-18 00:30
	:author: Gerald Richter
	:see: http://www.scipy.org/mailinglists/mailman?fn=scipy-user/2005-August/005141.html
	:see: http://www.iamg.org/naturalneighbour.html
	:todo:
	 - Need to find argument for keeping initialize.  If it isn't found, get rid of it!  There is some arguments for keeping initialize.
		- it may be convenient, to keep the data in the object, forgetting
		  about it in the instanciating routine, 
		- when using the call to the object, it behaves just like a function 
		  that is smoothly defined.
		- an interpolation is usually required many times, so the
		  instanciation and size-checking stuff is run only once.
	 - what happens, if I supply shapes of (x_new, y_new) e.g. (1,1) or (2,1) or (1,2) in Grid mode ?
	 - add nearest method
	 - supply an option for clipping the values outside the range. (in fill_value = Clip will return reduced grid of interpolated, plus the new grid)
"""
	from numpy import sometrue, asarray, transpose, atleast_1d
	# need masked arrays if stuff gets too big.
	#import MA
	
	# define the modes for interpolation
	#   'Grid'  gives results for a full combination of 
	#	   all x-points with all y-points
	#   'Point' gives results only for the pairs of points
	op_modes = ('Grid','Point')
	#self.avail_methods = ('linear', 'nearest')
	avail_methods = ('linear')

	# initialization
	def __init__(self,x,y,z,kind='linear',
				 copy=1,bounds_error=0,fill_value=None):
		"""Initialize a 2d linear interpolation class
		
		Input:
		  x,y  - 1-d arrays: defining 2-d grid or 2-d meshgrid 
							 have to be ascending order
		  z	- 2-d array of grid values
		  kind - interpolation type ('nearest', 'linear', 'cubic', 'spline')
		  copy - if true then data is copied into class, otherwise only a
				   reference is held.
		  bounds_error - if true, then when out_of_bounds occurs, an error is
						  raised otherwise, the output is filled with
						  fill_value.
		  fill_value - if None, then NaN, otherwise the value to fill in
						outside defined region.
		"""
		self.copy = copy
		self.bounds_error = bounds_error
		if fill_value is None:
			self.fill_value = array(0.0) / array(0.0)
		else:
			self.fill_value = fill_value

		if kind not in self.avail_methods:
			raise NotImplementedError, "Only "+ \
				str(self.avail_methods)+ \
				"supported for now."

		## not sure if the rest of method is kosher
		# checking the input ranks
		# shape z:
		#   x: columns, y: rows
		if rank(z) != 2:
			raise ValueError, "z Grid values is not a 2-d array."
		(rz, cz) = shape(z)
		if min(shape(z)) < 3:
			raise ValueError, "2d fitting a Grid with one extension < 3"+\
					"doesn't make too much of a sense, don't you think?"
		if (rank(x) > 1) or (rank(y) > 1):
			raise ValueError, "One of the input arrays is not 1-d."
		if (len(x) != rz) or (len(y) != cz):
			print "len of x: ", len(x)
			print "len of y: ", len(y)
			print "shape of z: ", shape(z)
			raise ValueError, "Length of X and Y must match the size of Z."

		# TODO: could check for x,y input as grids, and check dimensions

		# TODO: check the copy-flag
		#	   offer some spae-saving alternatives		
		#self.x = atleast_1d(x).copy()
		self.x = atleast_1d(x).astype(x.typecode())
		self.x.savespace(1)
		#self.y = atleast_1d(y).copy()
		self.y = atleast_1d(y).astype(y.typecode())
		self.y.savespace(1)
		#self.z = array(z, copy=self.copy)
		self.z = array(z, z.typecode(), copy=self.copy, savespace=1)


	# the call
	def __call__(self, xi, yi, mode='Grid'):
		"""
		Input:
		  xi, yi	  : 1-d arrays defining points to interpolate.
		  mode		: 'Grid': (default)
								calculate whole grid of x_new (x) y_new
								points, returned as such
						'Point' : take the [x_new, y_new] tuples and
								return result for each
		Output:
		  z : 2-d array (grid) of interpolated values; mode = 'Grid'
			  1-d array of interpol. values on points; mode = 'Point'
		"""
		
		if mode not in self.op_modes:
			raise NotImplementedError, "Only "+ \
				str(self.op_modes)+ \
				"operation modes are supported for now."

		# save some space
		# TODO: is this typing good?
		xi = atleast_1d(xi).astype(float32)
		yi = atleast_1d(yi).astype(float32)
		# TODO: check dimensions of xi, yi?
		#XI = MA.array(xi);
		#YI = MA.array(yi);
		XI = xi; YI = yi;
		X = self.x; Y = self.y;
		Z = self.z

		# TODO: move this to init ?
		xtable = X;
		ytable = Y;
		ytlen = len (ytable);
		xtlen = len (xtable);

		# REMARK: the octave routine sets the indices one higher if
		#	   values are equal, not lower, as searchsorted() does.
		#	   changed and verified behaviour, result only 
		#		   differed at O(1e-16). 
		#   this is the more exact and octave identical approach
		eqx = sum(X == reshape(repeat(XI,(len(X))), (len(X), len(XI))))
		# get x index of values in XI
		xidx = clip( (searchsorted(X,XI) + eqx),1,len(X)-1 )-1
		eqy = sum(Y == reshape(repeat(YI,(len(Y))), (len(Y), len(YI))))
		# get y index of values in YI
		yidx = clip( (searchsorted(Y,YI) + eqy),1,len(Y)-1 )-1
		
		# get the out of bounds
		(out_of_xbounds, out_of_ybounds) = \
								self._check_bounds(XI, YI)

		# generate an mgrid from the vectors
		#   transforming to full grid shapes
		( X, Y) = meshgrid( X, Y)
		( XI, YI) = meshgrid( XI, YI)
		"""
		if mode == 'Point':
			XI = MA.masked_array( XI, 
				mask=eye(shape(XI)[0], shape(XI)[1]).astype('b') )
			YI = MA.masked_array( YI, 
				mask=eye(shape(YI)[0], shape(YI)[1]).astype('b') )
			X = MA.masked_array( X, 
				mask=eye(shape(X)[0], shape(X)[1]).astype('b') )
			Y = MA.masked_array( Y, 
				mask=eye(shape(Y)[0], shape(Y)[1]).astype('b') )
		print X.mask()
		print X.compressed()
		"""

		# calculating the shifted squares
		a = (Z[:-1, :-1]);
		b = ((Z[:-1, 1:]) - a);
		c = ((Z[1:, :-1]) - a);
		d = ((Z[1:, 1:]) - a - b - c);

		# TODO: write an index take method
		it1 = take(take(X, xidx,axis=1), yidx, axis=0)
		Xsc = (XI - it1) / \
			  ( take(take(X,(xidx+1),axis=1), yidx, axis=0) - it1 )
		Xsc = transpose(Xsc)
		it2 = take(take(Y, xidx,axis=1), yidx, axis=0)
		Ysc = (YI - it2) / \
			  ( take(take(Y,xidx,axis=1), (yidx+1), axis=0) - it2 )
		Ysc = transpose(Ysc)
		#it1 = take(take(MA.filled(X,0), xidx,axis=1), yidx, axis=0)
		#Xsc = (MA.filled(XI,0) - it1) / \
		#	  ( take(take(MA.filled(X,0),(xidx+1),axis=1), yidx, axis=0) - it1 )
		#Xsc = MA.transpose(Xsc)
		#it2 = take(take(MA.filled(Y,0), xidx,axis=1), yidx, axis=0)
		#Ysc = (MA.filled(YI,0) - it2) / \
		#	  ( take(take(MA.filled(Y,0),xidx,axis=1), (yidx+1), axis=0) - it2 )
		#Ysc = MA.transpose(Ysc)

		# apply plane equation
		ZI = take( take(a,yidx,axis=1), xidx, axis=0) + \
				take(take(b,yidx,axis=1), xidx, axis=0) * Ysc + \
				take(take(c,yidx,axis=1), xidx, axis=0) * Xsc + \
				take(take(d,yidx,axis=1), xidx, axis=0) * (Ysc * Xsc)

		# do the out of boundary masking
		oob_mask = logical_or( transpose(resize(out_of_xbounds, 
						(shape(ZI)[1], shape(ZI)[0])) ),
					resize(out_of_ybounds, shape(ZI)) )
		#print "oob mask: \n", oob_mask, shape(oob_mask)
		# blind the oob vals i
		# - NOT NEEDED ANYMORE?
		#ZI = ZI*logical_not(oob_mask)
		# set the fill values
		putmask( ZI, oob_mask, self.fill_value)

		# correction for the scalar behaviour in calculations
		#   (dont return full interpolation grid for single values 
		#   in xi or yi)
		ZI = take( take( ZI, range(len(xi)), 0), range(len(yi)), 1)
		#ZI[:len(xi),:len(yi)]

		if mode == 'Point':
			ZI = diag( ZI)

		return (ZI)


	def _check_bounds(self, x_new, y_new):
		# If self.bounds_error = 1, we raise an error if any x_new values
		# fall outside the range of x.  
		# Otherwise, we return arrays indicating
		# which values are outside the boundary region.  

		# TODO: better use min() instead of [0],[-1]?
		below_xbounds = less(x_new, self.x[0])
		above_xbounds = greater(x_new,self.x[-1])
		below_ybounds = less(y_new, self.y[0])
		above_ybounds = greater(y_new,self.y[-1])
		#  Note: sometrue has been redefined to handle length 0 arrays
		# !! Could provide more information about which values are out of bounds
		if self.bounds_error and sometrue(below_xbounds):
			raise ValueError, " A value in x_new is below the"\
							  " interpolation range."
		if self.bounds_error and sometrue(above_xbounds):
			raise ValueError, " A value in x_new is above the"\
							  " interpolation range."
		if self.bounds_error and sometrue(below_ybounds):
			raise ValueError, " A value in y_new is below the"\
							  " interpolation range."
		if self.bounds_error and sometrue(above_ybounds):
			raise ValueError, " A value in y_new is above the"\
							  " interpolation range."
		# !! Should we emit a warning if some values are out of bounds.
		# !! matlab does not.
		out_of_xbounds = logical_or(below_xbounds,above_xbounds)
		out_of_ybounds = logical_or(below_ybounds,above_ybounds)

		return (out_of_xbounds, out_of_ybounds)

	# The following are cluges to fix brain-deadness of take and
	# sometrue when dealing with 0 dimensional arrays.
	# Shouldn't they go to scipy_base??

	_sometrue = sometrue
	def sometrue(a,axis=0):	
		x = asarray(a)
		if shape(x) == (): x = x.flat
		return _sometrue(x)
	sometrue=staticmethod(sometrue)

	def reduce_sometrue(a):
		all = a
		while len(shape(all)) > 1:	
			all = sometrue(all)
		return all
	reduce_sometrue=staticmethod(reduce_sometrue)

	## indices does that too in some way
	def meshgrid( a, b):
		a = asarray(a)
		b = asarray(b)
		return resize(a,(len(b),len(a))), \
			transpose(resize(b,(len(a),len(b))))
	meshgrid=staticmethod(meshgrid)




def asciihist(it,numbins=10,minmax=None,eps=0):
	'''Create an ASCII histogram from an interable of numbers.

	:since: 2005-11-12
	:note: value must be strictly less than cutoff to be binned
	:note: unless eps>0, values >= minmax[1] are discarded
	:contact: alan DOT isaac AT gmail DOT com
	'''
	bins = range(numbins)
	freq = {}.fromkeys(bins,0)
	itlist=list(it)
	#sort the list before binning it
	itlist.sort()
	if minmax:
		#discard values that are outside minmax range
		itmin=minmax[0]
		itmax=minmax[1]
		while itlist[0]<itmin: itlist.pop(0)
		while itlist[-1]>=itmax+eps: itlist.pop()
	else:
		#bin all values
		itmin=itlist[0]
		itmax=itlist[-1]
		eps=1
	cutoffs = [itmin]
	bin_increment = (itmax-itmin)/numbins
	#fill all but the last bin
	for bin in bins[:-1]:
		cutoff = itmin+(bin+1)*bin_increment
		cutoffs.append(cutoff)
		while itlist and itlist[0]<cutoff:
			freq[bin]=freq[bin]+1
			#discard the binned item
			itlist.pop(0)
	#the rest go in the last bin
	freq[bins[-1]]=len(itlist)
	for bin in bins:
		print "%2.2f |"%(cutoffs[bin]) + "*"*freq[bin]

def pascal_triangle(n):
	'''The first n+1 rows of Pascal's triangle.

	:since: 2005-11-18
	:contact: alan DOT isaac AT gmail DOT com
	'''
	triangle = []
	for i in range(n+1):
		triangle.append([1]*(i+1))
		if i>1:
			for j in range(1,i):
				triangle[i][j] = triangle[i-1][j-1] + triangle[i-1][j]
	return triangle

def combinations(s,n):
	"""All combinations of n items from list x
	(in stable order).  From pytrix.py.

	:since: 2006-09-15
	:note: just delete 'list' to return a generator
	:contact: alan DOT isaac AT gmail DOT com
	"""
	s = list(s)
	depth = len(s)-n
	if n==0: return [[]] #list containing empty list
	if n==1: return list([si] for si in s) #list containing lists containing s items
	if depth == 0:
		return [s]
	return list( [s[i]]+list(r) for i in xrange(depth+1) for r in combinations(s[i+1:], n-1) )
	"""
	#old version
	all = []
	for i in xrange(depth+1):
	 	print i
	 	for r in combinations(s[i+1:], n-1) :
			print "concatenate:", [s[i]], r
			all.append([s[i]]+r)
	return all
	"""

def pascal_row(n):
	'''Row n (counting from 0) of Pascal's triangle.
	Equivalently: the coefficients of (a+b)^n.

	:author: Alan Isaac
	:since: 2005-11-17
	'''
	row = [1]*(n+1)
	for i in xrange(1,(n+1)//2):
		row[i] = n_take_k(n,i)
		row[n-i] = row[i]
	if (n+1)%2:
		i=(n+1)//2
		row[i] = n_take_k(n,i)
	return row

def n_take_k(n,k):
	'''Returns (n take k).

	:since: 2005-11-17
	'''
	assert(k<=n and k==int(k) and n==int(n)),"n=%f, k=%f"%(n,k)
	k = min(k,n-k)
	if k==0:
		c = 1
	else:
		c = n
		for i in xrange(1,k):
			c*=n-i
		for i in xrange(1,k):
			c//=i+1
	return c	

def stirling(x):
	"""Return real number:
	the value of Stirling's formula::

		\sqrt{2 \pi x} (x/e)^x

	:note: can be used to approximate factorial
	"""
	result = math.sqrt(2*math.pi)
	result *= math.sqrt(x)
	result *= math.pow(x/math.e,x)
	return result

def gosper(x):
	"""Return real number:
	Gosper's modification of Stirling's formula::

		\sqrt{(2x+1/3)\pi} (x/e)^x

	:note: Used to compute factorial.
	:see: http://mathworld.wolfram.com/StirlingsApproximation.html
	"""
	result = math.sqrt((2*x+1./3)*math.pi)
	result *= math.pow(x/math.e,x)
	return result

def factorial(n, exact=False):
	'''Returns number:
	n! (exact integer or real approximation)

	:date: 2008-07-15
	:since: 2005-11-17
	:note: uses Gosper's approximation for n>=10
	:note: for Python 2.6+, use math.factorial
	:see: http://www.luschny.de/math/factorial/approx/SimpleCases.html
	'''
	assert (n==int(n) and n>=0), "%s is not a positive integer"%(n)
	if n<15 or exact:
		fac = 1
		for i in xrange(n):
			fac *= i+1
	else:
		fac = gosper(n)
	return fac


def geneigsympos(A, B):
	""" Solves symmetric-positive-definite generalized
	eigenvalue problem Az=lBz.

	Takes two real-valued symmetric matrices A and B (B must also be
	positive-definite) and returns the corresponding generalized (but
	also real-valued) eigenvalues and eigenvectors. Return format: as
	in numpy.linalg.eig, tuple (l, Z); l is directly taken from eigh
	output (a 1-dim array of length A.shape[0] ?), and Z is an array
	or matrix (depending on type of input A) with the corresponding
	eigenvectors in columns (hopefully).
	Eigenvalues are ordered ascending (thanks to eigh).

	:author: Sven Schreiber <svetosch gmx.net>
	:since: 30 Jan 2006
	"""
	from numpy import asmatrix, asarray, linalg
	#fixme: input checks on the matrices
	LI = asmatrix(linalg.cholesky(B)).I
	C = LI * asmatrix(A) * LI.T
	evals, evecs = linalg.eigh(C)
	if type(A) == type(asarray(A)): output = "array"
	# A was passed as numpy-array
	else: output = "matrix"
	#but the evecs need to be transformed back:
	evecs = LI.T * asmatrix(evecs)
	if output == "array": return evals, asarray(evecs)
	else:   return asmatrix(evals), evecs






def matrix_rank(arr,tol=1e-8):
	"""Return the matrix rank of an input array.

	:author: Bill Baxter <wbaxter gmail.com>
	:author: Alan G. Isaac
	:date: 18 Feb 2006
	"""
	if not have_numpy:
		raise NotImplementedError('numpy required for this function')
	arr = np.asarray(arr)
	if len(arr.shape) != 2:
	    raise ValueError('Input must be a 2-d array or Matrix object.') 
	svdvals = np.linalg.svdvals(arr)
	return sum(np.where(svdvals>tol,1,0))

	

def stinemanInterp(xi,x,y,yp=None):
	""" STINEMANINTERP  Well behaved data interpolation.
		Given data vectors X and Y, the slope vector YP and a new abscissa vector XI
		the function  StinemanInterp(X,Y,YP,XI) uses Stineman interpolation
		to calculate a vector YI corresponding to XI.

		Here's an example that generates a coarse sine curve, then
		interpolates over a finer abscissa:

			x = linspace(0,2*pi,20);  y = sin(x); yp = cos(x)
			xi = linspace(0,2*pi,40);
			yi = stinemanInterp(x,y,yp,xi);
			plot(x,y,'o',xi,yi)

		The interpolation method is described in the article  A CONSISTENTLY WELL BEHAVED
		METHOD OF INTERPOLATION by Russell W. Stineman. The article appeared in the July 1980
		issue of Creative computing with a note from the editor stating that while they were
		"not an academic journal but once in a while something serious and original comes in"
		adding that this was "apparently a real solution" to a well known problem.

		For yp=None, the routine automatically determines the slopes using the "slopes" routine.

		X is assumed to be sorted in increasing order

		For values xi[j] < x[0] or xi[j] > x[-1], the routine tries a extrapolation.
		The relevance of the data obtained from this, of course, questionable...

		:date: 2006-03-30
		:author: Norbert Nemec, Institute of Theoretical Physics, University or Regensburg, April 2006
				 Norbert.Nemec at physik.uni-regensburg.de
				 (inspired by a original implementation by Halldor Bjornsson, Icelandic
				 Meteorological Office, March 2006 halldor at vedur.is)
	"""

	from pylab import asarray, zeros

	# Cast key variables as float.
	x=asarray(x,'d')
	y=asarray(y,'d')
	assert x.shape == y.shape
	N=len(y)

	if yp is None:
		yp = slopes(x,y)
	else:
		yp=asarray(yp,'d')

	xi=asarray(xi,'d')
	yi=zeros(xi.shape,'d')

	# calculate linear slopes
	dx = x[1:] - x[:-1]
	dy = y[1:] - y[:-1]
	s = dy/dx  #note length of s is N-1 so last element is #N-2

	# find the segment each xi is in
	# this line actually is the key to the efficiency of this implementation
	idx = x[1:-1].searchsorted(xi)
	# now we have generally: x[idx[j]] <= xi[j] <= x[idx[j]+1]
	# except at the boundaries, where it may be that xi[j] < x[0] or xi[j] > x[-1]

	# the y-values that would come out from a linear interpolation:
	yo = y[idx] + s[idx] * (xi - x[idx])

	# the difference that comes when using the slopes given in yp
	dy1 = (yp[idx]-s[idx]) * (xi - x[idx])	   # using the yp slope of the left point
	dy2 = (yp[idx+1]-s[idx]) * (xi - x[idx+1]) # using the yp slope of the right point

	dy1dy2 = dy1*dy2
	# The following is optimized for Python. The solution actually does more calculations than necessary
	# but exploiting the power of numpy, this is far more efficient than coding a loop by hand in Python
	yi = yo + dy1dy2 * (array(sign(dy1dy2),'i')+1).choose(
		(2*xi-x[idx]-x[idx+1])/((dy1-dy2)*(x[idx+1]-x[idx])),
		0.0,
		1/(dy1+dy2),
	)
	return yi


def slopes(x,y):
	"""SLOPES calculate the slope y'(x)
		Given data vectors X and Y SLOPES calculates Y'(X), i.e the slope
		of a curve Y(X). The slope is estimated using the slope obtained
		from that of a parabola through any three consecutive points.

		This method should be superior to that described in the appendix of
		A CONSISTENTLY WELL BEHAVED METHOD OF INTERPOLATION
		by  Russel W. Stineman (Creative Computing July 1980) in at least one aspect:

		Circles for interpolation demand a known aspect ratio between x- and y-values.
		For many functions, however, the abscissa are given in different dimensions,
		so an aspect ratio is completely arbitrary.

		The parabola method gives very similar results to the circle method for most
		regular cases but behaves much better in special cases

		:date: 2006-03-30
		:author: Norbert Nemec, Institute of Theoretical Physics, University or Regensburg, April 2006
				 Norbert.Nemec at physik.uni-regensburg.de
				 (inspired by a original implementation by Halldor Bjornsson, Icelandic
				 Meteorological Office, March 2006 halldor at vedur.is)
	"""

	from pylab import asarray, zeros

	# Cast key variables as float.
	x=asarray(x,dtype='d')
	y=asarray(y,dtype='d')

	yp=zeros(y.shape,dtype='d')

	dx=x[1:] - x[:-1]
	dy=y[1:] - y[:-1]
	dydx = dy/dx
	yp[1:-1] = (dydx[:-1] * dx[1:] + dydx[1:] * dx[:-1])/(dx[1:] + dx[:-1])
	yp[0] = 2.0 * dy[0]/dx[0] - yp[1]
	yp[-1] = 2.0 * dy[-1]/dx[-1] - yp[-2]
	return yp
 
	
		

def chebyu(N,x):
	'''
	:author: Norbert Nemec <Norbert.Nemec.list gmx.de>
	:date: 2005-04-24

	I checked the implementation of chebyu and found that it basically first
	calculates the coefficients from the generating function and then adds
	up the polynomial. In the numerical range of question, this means adding
	up huge numbers with alternating sign, producing bad numerical errors.  
	I found a ridiculously simple solution:
	'''
	previous = 0.0
	current = 1.0
	for n in range(N):
		previous, current = current, 2*x*current - previous
	return current


import sys, math
import numpy.linalg.linalg as la


def fnnls(XtX, Xty, tol = 0) :
	'''
	:author: Graeme O'Keefe, PhD, MACPSEM <gjok netspace.net.au>
	:date: 20050816
	:comments: below

	ported fnnls.m to fnnls.py::
	
		x, w = fnnls(XtX, Xty, tol)
	
	FNNLS	Non-negative least-squares.
	
	Adapted from NNLS of Mathworks, Inc.
	[x,w] = nnls(X, y)
	
	x, w = fnnls(XtX,Xty) returns the vector X that solves x = pinv(XtX) *Xty
	in a least squares sense, subject to x >= 0.
	Differently stated it solves the problem::

		min ||y - Xx|| if XtX = X'*X and Xty = X'*y.
	
	A default tolerance of TOL = MAX(SIZE(XtX)) * NORM(XtX,1) * EPS
	is used for deciding when elements of x are less than zero.
	This can be overridden with x = fnnls(XtX,Xty,TOL).
	
	[x,w] = fnnls(XtX,Xty) also returns dual vector w where
	w(i) < 0 where x(i) = 0 and w(i) = 0 where x(i) > 0.
	
	See also NNLS and FNNLSb

	Original Matlab code was written by:
	
	L. Shure 5-8-87
	Revised, 12-15-88,8-31-89 LS.
	(Partly) Copyright (c) 1984-94 by The MathWorks, Inc.

	Modified by R. Bro 5-7-96 according to
	Bro R., de Jong S., Journal of Chemometrics, 1997, 11, 393-401
	Corresponds to the FNNLSa algorithm in the paper
	
	Rasmus bro
	Chemometrics Group, Food Technology
	Dept. Dairy and Food Science
	Royal Vet. & Agricultural
	DK-1958 Frederiksberg C
	Denmark
	rb@kvl.dk
	http://newton.foodsci.kvl.dk/users/rasmus.html
	Reference:
	Lawson and Hanson, "Solving Least Squares Problems", Prentice-Hall, 1974.
	''' 
	def any(X)     : return len(np.nonzero(X)) != 0
	def find(X)    : return np.nonzero(X)
	def norm(X, d) : return max(np.sum(abs(X)))
	# initialize variables
	m = XtX.shape[0]
	n = XtX.shape[1]

	if tol == 0 :
		eps = 2.2204e-16
		tol = 10 * eps * norm(XtX,1)*max(m, n);
	#end

	P = np.zeros(n, np.Int16)
	P[:] = -1
	Z = np.arange(0,n)

	z = np.zeros(m, np.float32)
	x = np.array(P)
	ZZ = np.array(Z)

	w = Xty - np.dot(XtX, x)

	   # set up iteration criterion
	iter = 0
	itmax = 30 * n

	   # outer loop to put variables into set to hold positive coefficients
	while any(Z) and any(w[ZZ] > tol) :
		wt = w[ZZ].max()
		t = find(w[ZZ] == wt)
		t = t[-1:][0]
		t = ZZ[t]
		P[t] = t
		Z[t] = -1
		PP = find(P != -1)

		ZZ = find(Z != -1)
		if len(PP) == 1 :
			XtyPP = Xty[PP]
			XtXPP = XtX[PP, PP]
			z[PP] = XtyPP / XtXPP
		else :
			XtyPP = np.array(Xty[PP])
			XtXPP = np.array(XtX[PP, np.array(PP)[:,  np.NewAxis]])
			z[PP] = np.dot(XtyPP, la.generalized_inverse(XtXPP))
		#end
		z[ZZ] = 0

		# inner loop to remove elements from the positive set which no longer  belong
		while any(z[PP] <= tol) and (iter < itmax) :
			iter += 1
			iztol = find(z <= tol)
			ip = find(P[iztol] != -1)
			QQ = iztol[ip]

			if len(QQ) == 1 : alpha = x[QQ] / (x[QQ] - z[QQ])
			else :
				x_xz = x[QQ] / (x[QQ] - z[QQ])
				alpha = x_xz.min()
			#end

			x += alpha * (z - x)
			iabs = find(abs(x) < tol)
			ip = find(P[iabs] != -1)
			ij = iabs[ip]

			Z[ij] = np.array(ij)
			P[ij] = -1
			PP = find(P != -1)
			ZZ = find(Z != -1)

			if len(PP) == 1 :
				XtyPP = Xty[PP]
				XtXPP = XtX[PP, PP]
				z[PP] = XtyPP / XtXPP
			else :
				XtyPP = np.array(Xty[PP])
				XtXPP = np.array(XtX[PP, np.array(PP)[:,  np.NewAxis]])
				z[PP] = np.dot(XtyPP, la.generalized_inverse(XtXPP))
			#endif
			z[ZZ] = 0
		#end while
		x = np.array(z)
		w = Xty - np.dot(XtX, x)
	#end while

	return x, w

def test_fnnls():
	# test [x, w] = fnnls(Xt.X, Xt.y, tol)
	# to solve min ||y - X.x|| s.t. x >= 0
	X = np.array([[1, 10, 4, 10], [4, 5, 1, 12], [5, 1, 9, 20]],  np.float32)
	y = np.array([4, 7, 4], np.float32)
	Xt = X.transpose()
	x, w = fnnls(np.dot(Xt, X), np.dot(Xt, y))
	print 'X = ', X
	print 'y = ', y
	print 'x = ', x




class Histogram(object):
	"""Class constructor to compute weighted 1-D histogram.
	Usage: Histogram(data, bins=10, range=None, weights=None, normed=False)
	 
	 Input parameters
	 ---------------------------
		data:  Input array 
		bins:  Number of bins or the bin array(overides the range).
		range: A tuple of two values defining the lower and upper ends of the bin span. 
			   If no argument is given, defaults to (data.min(), data.max()).
		weights: Array of weights stating the importance of each data. This array must have the same shape as data. 
	
	Methods
	-------------  
		add_data(values, weights): Add values array to existing data and update bin count. This does not modify the histogram bining.
		optimize_binning(method): Chooses an optimal number of bin. Available methods are : Freedman, Scott. 
		score(percentile): Returns interpolated value at given percentile.
		cdf(x, method): Return interpolated cdf at x.
	
	Attributes
   ---------------- 
		freq: The resulting bin count. If normed is true, this is a frequency.  If normed is False, then freq is simply the number of data falling into each bin.
		cum_freq: The cumulative bin count.
		data: Array of data. 
		weights: Array of weights.
		s_data: Array of sorted data.
		
		range	 : Bin limits : (min, max)
		Nbins	 : Number of bins
		bin	   : The bin array (Nbin + 1)
		normed: Normalization factor. Setting it to True will normed the density to 1.
		weighted  : Boolean indicating whether or not the data is weighted.

	:License: MIT
	:Author: David Huard <david.huard gmail.com>

	:Changes log:

		- 2006, June 2: Completed object interface
		- May  : Small corrections to docstrings
		- April : Modified to use objects 
		- March : Creation

	:TODO:

		# Clean up the normed object in order to avoid calling __compute_cum_freq when it is changed.
		# Add a simple pdf method
		# Add 2D support
	"""
	from numpy import atleast_1d, linspace, ones, sort, float32, concatenate, diff, cross, array, size
	#TODO: must uncomment next line, but that requires scipy
	#from scipy.interpolate import interp1d

	def __init__(self, data, bins=10, range=None, weights=None, normed=False):
		self.__Init = True
		self.weights = weights
		self.data = data
		self.range = range
		self.__normed = normed
		if size(bins) == 1:
			self.Nbins = bins 
		else:
			self.bins = bins
			if range is not None:
				print 'The bin array assignment superseded the range assignment.'
		
		self.__compute()
		self.__empirical_cdf()
		self.__Init = False
		
	def __delete_value(self):
		"""Delete method."""
		raise TypeError, 'Cannot delete attribute.'
	
	def __set_value(self):
		raise TypeError, 'Cannot set attribute.'
	
	def range(): #---- range object ----
		doc = """A tuple of two values defining the lower and upper ends of the bin span. 
			   If no argument is given, defaults to (data.min(), data.max())."""
		def fget(self):
			return self.__range
		def fset(self, value):
			if value is None:
				self.__range = array((self.__data.min(), self.__data.max()*(1+1E-6)))
			else:
				value = atleast_1d(value)		
				if len(value) != 2:
					raise TypeError, 'Range must have two elements (min, max).'
				self.__range = value 
				if self.__Init is False:
					self.__compute()
		return locals()
	range = property(**range())
	
	
	def bins(): #---- bins object ----
		doc = "Bin array. A (n) array for n-1 bins. Calling this method updates the count."
		
		def fset(self, bin_array):
			"""Set method for bin attribute.""" 
			if size(bin_array) < 2:
				raise 'Bin array must contain at least two positions.'
			self.__bins=atleast_1d(bin_array)
			self.range = (self.__bins[0], self__bins[-1])
			if self.__Init is False:
				self.__compute()
		
		def fget(self):
			"""Get method for bin attribute."""
			return self.__bins
		
		return locals()
	bins = property(**bins())
	   

		
	def Nbins(): #---- Nbins object ----
		doc = "Number of bins. Setting this value updates the bin count."
		def fset(self, value):
			"""Set method for Nbins."""
			if (size(value) != 1):
				raise TypeError, 'Nbin must be a scalar.'
			else:
				self.__Nbins = value
				self.__bins = linspace(self.__range[0], self.__range[1], self.__Nbins+1) 
				if self.__Init is False:
					self.__compute()
				
		def fget(self):
			"""Get method for Nbins."""
			return self.__Nbins

		return locals()
	Nbins = property(**Nbins())
   

	
	def weighted(): #---- weighted object ----
		doc = "Boolean specifying whether or not the data is weighted." 
		def fget(self):
			return self.__weighted
		
		def fset(self, value):
			if (value == True) or (value == False):
				self.__weighted = value
				if self.__Init is False:
					self.__compute()
			else:
				raise TypeError, 'weighted must be a boolean (True/False).'
		return locals()
	weighted = property(**weighted())
		
	
	def normed(): #---- normed object ----
		doc = """
		Value specifying whether or not the frequency and cumulative frequency should be normalized. 
		If normed is True: norm=1
		If normed if False or 0: freq = number of values in each bin.
		If normed is a scalar: the bin count is scaled so that the area under the curve is equal to normed. 
		"""
		def fget(self):
			return self.__normed
	
		def fset(self, value):			 
			if size(value) != 1:
				raise TypeError, 'normed must be a boolean (True/False) or a scalar.'
			if value:
				self.__normed = value*1.
			else:
				self.__normed = value
			self.__compute()
										 
		return locals()
	normed = property(**normed())
	
	
	
	def weights(): #---- weights object ----
		doc = """Array of weights defining the relative importance of each datum."""
		def fset(self, value):
			"""Assigns weights to the data already present in the class attribute."""
			if value is None:
				self.weighted = False
				self.__weights = value				
			else :
				value = atleast_1d(value)
				if size(value) == size(self.__data):
					self.weighted = True
					if not self.normed:
						self.normed = True
				else:
					raise TypeError, 'The size of the weight array (%d) must be identical to the data size (%d).' % (size(weights), size(self.__data))
				if self.__Init is False:
					self.__compute()
			
		def fget(self):
			if self.__weights is None:
				print 'No weights are yet assigned.'
			else:
				return self.__weights
	
		def fdel(self):
			self.__weighted = False
			self.__weights = None
		return locals()
	weights =property(**weights())
	 
		
  
	def data(): #---- data object ----
		doc = "Array of values to bin."		
		def fget(self):
			return self.__data
	
		def fset(self, data):
			self.__data = atleast_1d(data)
			if self.__Init is False:
				self.__compute()
		return locals()
	data = property(**data())
	
	def freq(): #-----freq object-----
		doc = "Bin count (bin frequency if normalized)."
		def fget(self):
			return self.__freq
		return locals()
	freq = property(**freq())
		
	def cum_freq(): #-----freq object-----
		doc = "Cumulative bin count (cumulative bin frequency if normalized)."
		def fget(self):
			return self.__cum_freq
		return locals()
	cum_freq = property(**cum_freq())
	
	def add_data(self, data, weights=None):
		"""Adds data to the data and weight attributes and updates the bin count."""
		
		self.__data = concatenate(self.__data, data)
		if weights is not None:
			self.weighted = True
			if self.__weights is None:
				self.__weights = ones(len(data), dtype = float32)
			self.__weights = concatenate(self.__weights, weights)
		self.__compute()
		
	def __compute_cum_freq(self):
		"""Sort the data and store it internally. Puts cum_freq in the class attributes. """
		if not self.weighted:
			sd = sort(self.data)
			n = sd.searchsorted(self.bins)
			cf = n-n[0]
			self.__cum_freq = cf[1:]
		else:
			sd, sw = sort(zip(self.data,self.weights), axis=0).transpose()			
			n = sd.searchsorted(self.bins)
			cw = concatenate((atleast_1d(0),sw.cumsum()))
			self.__cum_freq = cw[n[1:]]
			self.__sorted_weights = sw
		self.__sorted_data = sd
		
	
	
	def __compute(self):
		"""Updates the bin count."""
		
		self.__compute_cum_freq()
		self.__freq = concatenate((atleast_1d(self.__cum_freq[0]), diff(self.__cum_freq)))
		if self.__normed:
			self.__normalize()
			
	def __normalize(self):
		"""Normalizes the frequency count so that the area under the curve is norm.
		Normalizes the cumulative frequency so that the largest value is norm."""
		N = sum(self.__freq*diff(self.__bins))
		self.__freq = self.__freq/N*self.__normed
		self.__cum_freq = self.__cum_freq*1./self.__cum_freq[-1]*self.__normed

	
	def optimize_binning(self, method='Freedman'):
		"""Find the optimal number of bins and update the bin count accordingly.
		Available methods : Freedman, Scott
		"""
		
		N = len(self.data)
		if method=='Freedman':
			IQR = self.score(75) - self.score(25) # Interquantile range (75% -25%)
			width = 2* IQR*N**(-1./3)
			
		elif method=='Scott':
			width = 3.49 * std(self.__data) * N**(-1./3)
		
		self.setNbin(self.range.ptp()/width)
 
		
	def __empirical_cdf(self, method='Weibull'):
		"""Compute the cdf and define an interpolation instance. 
		The cdf data and the interpolation instance are stored in a dictionnary.
		"""
		
		N = len(self.__data)
		i = linspace(1,N, N)
		self.__cdf = {}
		self.__interp_cdf={}
		self.__interp_score={}
		
		if method == 'Weibull':
			self.__cdf[method] = i/(N+1)
		elif method == 'Hazen':
			self.__cdf[method] = (i-0.5)/N
		elif method == 'California':
			self.__cdf[method] = (i-1)/N
		elif method == 'Chegodayev':
			self.__cdf[method] = (i-.3)/(N+.4)
		elif method == 'Cunnane':
			self.__cdf[method] = (i-.4)/(N+.2)
		elif method == 'Gringorten':
			self.__cdf[method] = (i-.44)/(N+.12)
		else:
			raise 'Unknown method. Choose among Weibull, Hazen, Chegodayev, Cunnane, Gringorten and California.'
		
		self.__interp_cdf[method] = interp1d(self.__sorted_data, self.__cdf[method])
		self.__interp_score[method] = interp1d(self.__cdf[method], self.__sorted_data)
	
	def cdf(self, x, method='Weibull'):
		"""Returns the cdf interpolated from an empirical cdf. 
		Available methods to compute cdf are Weibull, Hazen, Chegodayev, Cunnane, Gringorten and California."""
		
		if method not in self.__interp_cdf.keys():
			self.__empirical_cdf(method)
		
		return self.__interp_cdf[method](x)
		
	def score(self, percent, method='Weibull'):
		"""Returns the score at given percentile. 
		Available methods to compute cdf are Weibull, Hazen, Chegodayev, Cunnane, Gringorten and California. 
		The score is simply the inverted cdf."""

		# Do some checking
		percent = atleast_1d(percent)
		if percent.any() < 0:
			raise 'Percent must be positive.'
		elif percent.any() > 100:
			raise 'Percent must be smaller than 100.'
		
		if method not in self.__interp_score.keys():
			self.__empirical_cdf(method)
			
		return self.__interp_score[method](percent)

def locate_minima(x):
	''' Locate local minima in a 1-d array.

	Sample use::

		idx = locate_minima(x)
		minima = x[idx]

	:date: 2006-06-19
	'''
	from numpy import empty, asarray
	x = asarray(x)
	dx =  x[1:]-x[:-1]
	minima =  empty((len(x),),dtype=bool)
	minima[1:-1] = (dx[:-1]<=0) & (dx[1:]>=0)
	#handle endpoints
	minima[0]=dx[0]>=0
	minima[-1]=dx[-1]<=0
	return minima

def dist(A,B):
	''' Find distance between rows of A and rows of B.
	Result[i,j] = sqrt((A[i]-B[j])**2)

	:date: 2006-06-19
	'''
	assert A.shape[1]==B.shape[1]
	rowsA, rowsB = A.shape[0], B.shape[0]
	distanceAB = empty( [rowsA,rowsB] , dtype=float)
	if rowsA <= rowsB:
		temp = empty_like(B)
		for i in range(rowsA):
			#store A[i]-B in temp
			subtract( A[i], B, temp )
			temp *= temp
			#set distanceAB[i,:] = sqrt( temp.sum(axis=1) )
			sqrt( temp.sum(axis=1), distanceAB[i,:])
	else:
		temp = empty_like(A)
		for j in range(rowsB):
			#store A-B[j] in temp
			temp = subtract( A, B[j], temp )
			temp *= temp
			#set distanceAB[:,j] = sqrt( temp.sum(axis=1) )
			sqrt( temp.sum(axis=1), distanceAB[:,j])
	return distanceAB




def gen_convKern( self):
	'''
	Generate a (2-gaussian by 1-gaussian) convolution kernel with limits at
	multiples of the distribution sigmas -for 2Gauss: sigma(tail), for 1Gauss:
	sigma(core)

	:author: Gerald Richter
	:date: Thu Jun 22 16:43:58 CEST 2006
	:note: requires integrate_grid()
	'''
	tss = self.tstepSize;		# shortcut 4 stepsizes in [x, y]
	mSigMul = 5.0;		# the measurement sigma multiplier

	# have to get the max of the 2 distribs...
	# this will be the width of the tail distrib.
	#NOTE: this assumes, that the mean of the 2 gaussians is well within mSigMul * sigma(tail)

	# the limits of the convolution kernel are defined here.
	#		so that the kernel will have an extension up to 
	#		mSigMul[i] * sigma[i]
	mSigMul = [2.0, 3.0];		# had to reduce this here
	smear = self.paramInfo['measErrs'];
	# double gaussian model:
	#   mu(core), sigma(core), mu(tail), sigma(tail), 
	#   prob(core to tail)
	((mu1_c, sig1_c), (mu1_t, sig1_t), c2t_P1) = smear[0];
	# single gaussian
	(mu2_c, sig2_c) = smear[1];
	
	widths = c_[[sig1_t, sig2_c]]*mSigMul;
	convkern_min = -widths;   # lower borders for both times
	convkern_max = +widths;   # upper borders for both times
	print "ckmin", convkern_min
	print "ckmax", convkern_max

	# steps within mSigMul sigmas on scale of the convolution times
	ck5sigSteps = \
		[ max(1, ceil(widths[0]/ tss[0]) ), 
		max(1, ceil(widths[1]/ tss[1]) ) ];

	### convolution kernel generation
	ck5S = ck5sigSteps		# shortcut
	print "calculated conv kern steps:", ck5S

	self.convKGrid = zeros([3,2*ck5S[0] + 1, 2*ck5S[1] + 1],'d')
	self.convKGrid[:2] = mgrid[ 
		-ck5S[0]*tss[0]:ck5S[0]*tss[0]:(2*ck5S[0] + 1)*1j,
		-ck5S[1]*tss[1]:ck5S[1]*tss[1]:(2*ck5S[1] + 1)*1j ]
	ckg = self.convKGrid	# shortcut
	# make 3 objects of values for each coord.
	#   well ordered	[[t1.1,t1.1,....],[t1.2,t1.2,....],..]
	#		[[t2.1,t2.2,....],[t2.1,t2.2,....],..]
	#		[[z11, z12, ....],[z21, z22, ... ],..]

	# !!! paramInfo['dataMode'] == 't1dt_2G1G' !!!
	gauss2d = lambda x,y: \
		( c2t_P1*stats.norm(mu1_c,sig1_c).pdf(x) +
		(1.0-c2t_P1)*stats.norm(mu1_t,sig1_t).pdf(x) ) * \
		stats.norm( mu2_c, sig2_c).pdf(y); 

	ckg[2] = reshape( gauss2d( ravel(ckg[0]), ravel(ckg[1]) ),
		shape(ckg[2]) )
	ckg[2] /= self.integrate_grid( ckg)		# normalize

	#plotting that:
	# levels, colls = contour(ftr.convKGrid[0,:,0], ftr.convKGrid[1,0,:],
	# ftr.convKGrid[2,:,:])
	# clabel(colls, levels, fontsize=9, inline=1, fmt='%1.2e')
	#or:
	#im = imshow(ftr.convKGrid[2], interpolation='bilinear',
	#origin='lower',cmap=cm.hot, extent=( min(ftr.convKGrid[0,:,0]),
	#max(ftr.convKGrid[0,:,0]), min(ftr.convKGrid[1,0,:]),
	#max(ftr.convKGrid[1,0,:]) ) )


def integrate_grid( self, grid):
	'''
	:author: Gerald Richter
	:date: Thu Jun 22 16:43:58 CEST 2006
	:note: see integrate_grid()
	'''
	xrange = grid[0,:,0]	# take first x range vector
	yrange = grid[1,0,:]	# take first y range vector

	# smart choice of first integration axis (the smaller one)
	if ( shape(grid)[2] > shape(grid)[1]):
		#print "choosing first integration axis: X"
		intmarg = zeros([shape(grid)[2]],'d')
		# get y extension
		for y in range(shape(grid)[2]):
			#print grid[0,:,y]	# the x coords along each y-axis
			#print grid[2,:,y]	# and pdf values
			intmarg[y] = integrate.trapz( grid[2,:,y], xrange)
			#print intmarg[y]
		return integrate.trapz( intmarg, yrange) 

	else:
		#print "choosing first integration axis: Y"
		intmarg = zeros([shape(grid)[1]],'d')
		for x in range(shape(grid)[1]):
			intmarg[x] = integrate.trapz( grid[2,x,:], yrange)
		return integrate.trapz( intmarg, xrange) 


def makeGaussian(size, fwhm = 3):
	""" Make a square gaussian kernel.

	size is the length of a side of the square
	fwhm is full-width-half-maximum, which
	can be thought of as an effective radius.
	:author: James Carroll <mrmaple gmail.com>
	:date: 2006-06-22
	"""
	x = arange(0, size, 1, float32)
	y = x[:,NewAxis]
	x0 = y0 = size // 2
	return exp(-4*log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)


class Stats:
	'''
	Calculate standard statistics while ignoring data gaps,
	which may be indicated by nan values or by masked array input.

	Usages::

		1) (m, s, n, med) = Stats(y)(median=True)
		2) Sy = Stats(y)
		   m = Sy.mean	  # mean
		   s = Sy.std	   # standard deviation
		   n = Sy.N		 # number of valid points
		   med = Sy.median  # median
		   ydm = Sy.demeaned  # de-meaned input array

	In the first case we call the instance to get all the statistics at
	once; in the second we access the statistics as attributes.  In
	the latter case, subsequent accesses are cheap because the value
	is stored in the instance.  Each statistic is calculated
	only the first time it is requested.

	Caution: the outputs are references to arrays that may be needed
	for subsequent calculations, so don't modify them unless you
	have already done all calculations.

	For usage (1), the argument median=True results in all four
	statistics; median=False, the default, calculates and outputs
	only the first three.

	The constructor has the following keyword arguments and defaults::
	
		axis=0 : specifies the axis along which the stats are calculated
		squeeze=True: stats for an N-dimensional input have N-1
				dimensions if True, N dimensions if False.
				If False, the stats are broadcastable to the dimensions
				of the input array.
				See also the broadcastable method.
		masked='auto' : True|False|'auto' determines the output;
				if True, output will be a masked array;
				if False, output will be an ndarray with nan used
							as a bad flag if necessary;
				if 'auto', output will match input
				(The N attribute is an ndarray in any case.)

	:author: Eric Firing <efiring hawaii.edu>
	:date: 2006-07-14
	:note: compare functionality (but not interface) to Matlabs mstdgap.m
	:note: lightly tested, so use with care
	'''
	def __init__(self, y, axis=0, squeeze=True, masked='auto'):
		'''
		See the class docstring.
		'''
		self._axis = axis
		self._squeeze = squeeze
		if hasattr(y, 'mask'):
			mask = np.ma.getmaskarray(y)
		else:
			mask = np.isnan(y)
		if masked == True or (masked == 'auto' and hasattr(y, 'mask')):
			self._nanout = False
		else:
			self._nanout = True
		self._y = np.ma.array(y, mask=mask, fill_value=0)
		self._mask = mask
		self._mean = None
		self._std = None
		self._median = None
		nbad = self._mask.sum(axis=self._axis)
		self._N = self._y.shape[self._axis] - nbad
		self.b_shape = list(self._y.shape)   # broadcastable shape
		self.b_shape[axis] = 1


	def __call__(self, median=False):
		if median:
			return self.mean, self.std, self.N, self.median
		else:
			return self.mean, self.std, self.N

	def broadcastable(self, x):
		'''
		Change the shape of a summary statistic (mean, N, std,
		or median) so that it is broadcastable to the shape of
		the input array.  This is needed only if the class
		constructor was called with squeeze=False.
		'''
		# as of 2006/07/08 the view method is not implemented
		#return x.view().reshape(*self.b_shape)
		if hasattr(x, 'mask'):
			return np.ma.array(x, copy=False).reshape(*self.b_shape)
		else:
			return x.view().reshape(*self.b_shape)

	def get_N(self):
		if self._squeeze:
			return self._N
		else:
			return self.broadcastable(self._N)
	N = property(get_N)

	def calc_mean(self):
		if self._mean is None:
			self._mean = self._y.sum(axis=self._axis)/self._N
		return self._mean

	def get_mean(self):
		m = self.calc_mean()
		if self._nanout:
			m = m.filled(fill_value=np.nan)
		if self._squeeze:
			return m
		else:
			return self.broadcastable(m)
	mean = property(get_mean)

	def calc_std(self):
		if self._std is None:
			m = self.broadcastable(self.calc_mean())
			ss = (self._y - m)**2
			n = np.ma.masked_where(self._N <= 1, self._N-1)
			self._std = np.sqrt(ss.sum(axis=self._axis)/n)
		return self._std

	def get_std(self):
		s = self.calc_std()
		if self._nanout:
			s = s.filled(fill_value=np.nan)
		if self._squeeze:
			return s
		else:
			return self.broadcastable(s)
	std = property(get_std)

	def calc_median(self):
		if self._median is None:
			ysort = np.ma.sort(self._y, axis=self._axis)
			ii = np.indices(ysort.shape)[self._axis]
			ngood = self.broadcastable(self._N)
			i0 = (ngood-1)//2
			i1 = ngood//2
			cond = np.logical_or(i0==ii, i1==ii)
			m0 = np.ma.where(cond, ysort, 0)
			m = m0.sum(axis=self._axis)/cond.sum(axis=self._axis)
			self._median = m
		return self._median

	def get_median(self):
		m = self.calc_median()
		if self._nanout:
			m = m.filled(fill_value=np.nan)
		if self._squeeze:
			return m
		else:
			return self.broadcastable(m)
	median = property(get_median)

	def get_demeaned(self):
		m = self.broadcastable(self.calc_mean())
		y = self._y - m
		if self._nanout:
			y = y.filled(fill_value=np.nan)
		return y
	demeaned = property(get_demeaned)

def pnpoly(verts,point):
	"""Check whether point is in the polygon defined by verts.
	
	verts - 2xN array
	point - (2,) array
	
	:see: http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html	
	:see: test_poly
	:author: Stefan van der Walt <stefan sun.ac.za>
	:date: Jul 07, 2006
	"""
	
	verts = verts.astype(float)
	x,y = point
	
	xpi = verts[:,0]
	ypi = verts[:,1]	
	# shift
	xpj = xpi[np.arange(xpi.size)-1]
	ypj = ypi[np.arange(ypi.size)-1]
	
	possible_crossings = ((ypi <= y) & (y < ypj)) | ((ypj <= y) & (y < ypi))

	xpi = xpi[possible_crossings]
	ypi = ypi[possible_crossings]
	xpj = xpj[possible_crossings]
	ypj = ypj[possible_crossings]
	crossings = x < (xpj-xpi)*(y - ypi) / (ypj - ypi) + xpi
	return sum(crossings) % 2

# tests for pnpoly
from numpy.testing import NumpyTest, NumpyTestCase
class test_poly(NumpyTestCase):
	def test_square(self):
		v = np.array([[0,0], [0,1], [1,1], [1,0]])
		assert(pnpoly(v,[0.5,0.5]))
		assert(not pnpoly(v,[-0.1,0.1]))
	def test_triangle(self):
		v = np.array([[0,0], [1,0], [0.5,0.75]])
		assert(pnpoly(v,[0.5,0.7]))
		assert(not pnpoly(v,[0.5,0.76]))
		assert(not pnpoly(v,[0.7,0.5]))

