'''GAUSS command look alikes for `numpy`

:author: Alan G. Isaac, except where otherwise specified.
:copyright: 2005 Alan G. Isaac, except where another author is specified.
:license: `MIT license`_
:see: `pytrix.py <http://www.american.edu/econ/pytrix/pytrix.py>`
:see: `pyGAUSS.py <http://www.american.edu/econ/pytrix/pyGAUSS.py>`
:see: tseries.py
:see: unitroot.py
:see: pytrix.py
:see: IO.py
:since: 2004-08-04
:note: Current location: http://www.american.edu/econ/pytrix/pyGAUSS.py
:note: Should work fine with Numeric or numarray
:contact: aisaac AT american.edu http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '20050420'

import numpy
N = numpy

#assumes scipy has been imported as *
#from RandomArray import standard_normal as randn #not necessary if using scipy
#from RandomArray import random as rand #not necessary if using scipy

#------------- Look alikes written by Alan Isaac ----------------------#

#cols: number of columns (size of last dimension, i.e., axis -1)
def cols(x):
	if not isinstance(x,numpy.ndarray):
		x = numpy.asarray(x)
	return x.shape[-1]

#cumsumc: cumulative sum along each column
def cumsumc(x):
	if not isinstance(x,numpy.matrix):
		x = numpy.atleast_2d(x)
	return x.cumsum(axis=-2)

#cumsumc: cumulative product along each column
def cumprodc(x):
	if not isinstance(x,numpy.matrix):
		x = numpy.atleast_2d(x)
	return x.cumprod(axis=-2)

def design(x,colidx='gauss'):
	'''Create design matrix.
	Output::

		y an RxK array, where R=rows(x), K = max(x)
		y is all zeros except y[r,k]=1 iff x[r]=k

	:note: default is to input GAUSS column numbers
          (!!NOT!! Python indices)
	:param `x`: list of column numbers
	'''
	xmax = N.round_(x).max()
	print xmax
	if (colidx=='gauss'):
		return (N.round_(x).reshape((-1,1))==N.arange(1,xmax+1)).astype(int)
	else:
		return (N.round_(x).reshape((-1,1))==N.arange(xmax+1)).astype(int)

#diag: diagonal of matrix as column vector (2D only!)
def diag(x):
	if not isinstance(x,numpy.matrix):
		x = numpy.asanyarray(x)
		assert(len(x.shape)==2), "For 2-d arrays only."
		return x.diagonal(offset=0,axis1=-2,axis2=-1).reshape((-1,1))
	else:
		return x.diagonal().T

#diagrv: insert v as diagonal of matrix x (2D only!)
def diagrv(x, v, copy=True):
	if (len(x.shape) != 2):
		raise ValueError("For 2-d arrays only.")
	x = numpy.matrix( x, copy=copy )
	stride = 1 + x.shape[1]
	x.flat[ slice(0,None,stride) ] = v
	return x

#prodc: product down colums (2D only!)
def prodc(x):
	if not isinstance(x, numpy.matrix):
		x = numpy.asarray(x)
		if (len(x.shape) != 2):
			raise ValueError("For 2-d arrays only.")
		return x.prod(axis=-2).reshape((-1,1))
	else:
		return x.prod(axis=-2).T

#rndn: 2-d array of standard normals
def rndn(r,k):
	return numpy.randn(int(r),int(k))

#rndu: 2-d array of standard uniforms
def rndu(r,k):
	return numpy.rand(int(r),int(k))

#rows: number of rows (1st dimension, axis 0)
def rows(x):
	if not isinstance(x,numpy.ndarray):
		x = numpy.asarray(x)
	return x.shape[0]

#seqa: n element additive sequence from start by inc
def seqa(start,inc,n):
	return numpy.mat(start+inc*numpy.arange(n)).T

#seqm: n element multiplicative sequence from start by inc
def seqm(start,inc,n):
	return numpy.mat(start*inc**N.arange(n)).T

#sortind: return sorted index of x (ZERO based!)
def sortind(x):
	x = numpy.asarray(x)
	sortidx = x.flat.argsort().reshape(x.shape)
	return sortidx

#sumc: sum down colums (2D only!)
def sumc(x): return N.asarray(x).sum(axis=-2).reshape((-1,1))

#trimr: trim t rows from top and b rows from bottom of array or list
def trimr(x,t,b):
	xrows=shape(x)[0]
	if t+b>=xrows:
        	raise ValueError, 'Input array has only '+str(xrows)+' rows.'
	return array(x[t:xrows-b],copy=1)


#sortc:   sort array on specified column NUMBER
#         NOT (!!) on column *index* (=colNUM-1)'''
# Format:    y = sortc(x,colNUM)
# Input:     x        RxC array
#            colNUM   integer 
# Output:    y        RxC array
# Remarks:   sorts on column *NUMBER* 
#            (starting at 1, following GAUSS convention)
#	    NOT (!!) on column *index* (=colNUM-1)
# Date:      5 Aug 2004
def sortc(x,colNUM):
	if not colNUM in range(1,1+shape(x)[1]):
        	raise ValueError, 'Index out of range.'
	return take(x,argsort(N.asarray(x)[:,colNUM-1],0))

#rotater: rotate row elements
# Format:    y = rotater(x,r)
#            rotater(x,r,inplace=True)
# Input:     x           RxK array
#            rotateby    size R integer array, or integer (rotation amounts)
#            inplace     boolean (default is False -> copies data)
# Output:    y           RxK array:
#                          rows rotated by rotateby
#                        or None (if inplace=True)
# Remarks:   Intended for use with 2d arrays.
#            rotateby values are positive for rightward rotation,
#	               negative for leftward rotation
# :date:   24 Feb 2006
def rotater(x,rotateby,inplace=False) :
	if not isinstance(x,numpy.ndarray):
		x = numpy.asarray(x)
	assert(len(x.shape)==2), "For 2-d arrays only."
	xrotate = numpy.array(x,copy=(not inplace)) 
	xrows = xrotate.shape[0]
	xcols = xrotate.shape[1]
	#make an iterater of row shifts
	if isinstance(rotateby,int):
		from itertools import repeat
		rowshifts = repeat(rotateby,xrows)
	else:
		rowshifts = numpy.asarray(rotateby)
		assert(rowshifts.size==xrows), "rotateby must match rows(x)"
		rowshifts = rowshifts.flat
	#perform rotation on each row
	for rownum in xrange(xrows):
		rs=rowshifts.next()
		#normalize the rowshift offset (works for negative numbers!)
		rs %= xcols       #xcols>0 --> rs>=0
		#do nothing if rs==0
		if rs>0:
			xrotate[rownum] = numpy.concatenate([xrotate[rownum][-rs:],xrotate[rownum][:-rs]])
	if inplace:
		return None
	else:
		return xrotate




#shiftr: shift row elements and fill with fv
# Format:    y = shiftr(x,shiftby,fv)
# Input:     x        RxC array
#            shiftby  Rx1 array or scalar (shift amounts)
#            fv       Rx1 array or scalar (fill values)
# Output:    y        RxC array:
#                       rows shifted by shiftby
#                       rows filled with fill
# Remarks:   Intended for use with 2D arrays.
#            Shiftby values positive for right shift,
#	        negative for left shift
#            The fill values replace y values.
#	    Unlike GAUSS: cycles over shiftby and fv,
#	     so no checking for conformability.
# Author: Alan G Isaac (aisaac AT american DOT edu)
# Date:   4 Aug 2004
def shiftr(x,shiftby,fv,copydata=True) :
	import itertools
	xs = numpy.asarray(x,copy=copydata)
	if rank(xs)==1:
		xs=[xs]
	else:
		assert(len(xs.shape)==2), "For 2-d arrays only."
	xrows = xs.shape[0]
	xcols = xs.shape[1]
	#limit shift to number of columns
	sn=itertools.cycle(clip(ravel([shiftby]),-xcols,xcols))
	f=itertools.cycle(ravel([fv]))
	for r in range(xrows):
		s=sn.next()
		if s>0:
			xs[r]=concatenate((N.asarray([f.next()]*s),xs[r][:-s]),0)
		if s<0:
			xs[r]=concatenate((xs[r][-s:],N.asarray([f.next()]*abs(s))),0)
	return xs

#subvec: Extracts an N elements from an NxK array, by column index
# Format: y = subvec(x,col_id)
# Input:
#   x       2-d array with shape (N,K)
#   col_id  1-d integer array of column indices
# Output: y[i] = x[i,ci[i]].
# :date: 20060224
def subvec(x,col_id):
	xrows,xcols = x.shape
	assert(xrows==len(col_id))
	idx = xcols*numpy.arange(xrows)+numpy.asarray(col_id)
	return x.flat[idx].transpose()


#vec: vectorize columns of 2-D array (or matrix)
# Format:    y = vec(x)
# Input:     x        RxK 2-D array (or matrix)
# Output:    y        (RK)x1 2-D array (or matrix):
#                       stacked columns of x
# :note:   ravel OK for non-contiguous arrays
# :author: Alan G Isaac (aisaac AT american DOT edu)
# :since:  20050420
# :date:   20060224
def vec(x):
	assert(len(x.shape)==2), "For 2-d arrays/matrices only."
	return x.transpose().ravel().reshape((-1,1))

#vecr: vectorize rows of 2-D array (or matrix)
# Format:    y = vecr(x)
# Input:     x        RxK 2-D array (or matrix)
# Output:    y        (RK)x1 2-D array (or matrix):
#                       stacked rows of x
# :author: Alan G Isaac (aisaac AT american DOT edu)
# :since:  20050420
# :date:   20060224
def vecr(x):
	assert(len(x.shape)==2), "For 2-d arrays/matrices only."
	return x.reshape((-1,1))




#------------- Look alikes written by others (please contribute!) -------------#
#nothing yet


#------------- Other useful stuff (please contribute!) -------------#



def kroneckerproduct(a,b):
	'''Compute a otimes b where otimes is the Kronecker product operator.

	
	Note: the Kronecker product is also known as the matrix direct product
	or tensor product.  It is defined as follows for 2D arrays a and b
	where shape(a)=(m,n) and shape(b)=(p,q):
	c = a otimes b  => cij = a[i,j]*b  where cij is the ij-th submatrix of c.
	So shape(c)=(m*p,n*q).

	:Parameters:
	 - `a`: 2-D array
	 - `b`: 2-D array
	:see: http://en.wikipedia.org/wiki/Kronecker_product
	:see: http://www.scipy.org/mailinglists/mailman?fn=scipy-user/2003-September/002138.html
	:author: Nils Wagner
	:author: Alan G. Isaac
	:date: 2004-08-12
	:copyright: public domain
	:since: 2003-09-03
	:note: Contributed to numarray in Sept 2003.

	>>> print kroneckerproduct([[1,2]],[[3],[4]])
	[[3 6]
	 [4 8]]
	>>> print kroneckerproduct([[1,2]],[[3,4]])
	[ [3 4 6 8]]
	>>> print kroneckerproduct([[1],[2]],[[3],[4]])
	[[3]
	 [4]
	 [6]
	 [8]]
	'''
	a, b = asarray(a), asarray(b)
	if not (len(shape(a))==2 and len(shape(b))==2):
        	raise ValueError, 'Input must be 2D arrays.'
	if not a.iscontiguous():
		a = reshape(a, a.shape)
	if not b.iscontiguous():
		b = reshape(b, b.shape)
	o = outerproduct(a,b)
	o.shape = a.shape + b.shape
	return concatenate(concatenate(o, axis=1), axis=1)
	

#varlagsold: old version, won't work on lists
#see pytrix for new version
def varlagsold(var,lags):
    xlags = N.transpose(shiftr(N.transpose(kron(ones((1,lags)),var)),kron(seqa(1-lags,1,lags),ones((cols(var),1))),-9999))
    return trimr(var,lags,0),trimr(xlags,0,lags)

