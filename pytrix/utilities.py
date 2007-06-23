'''
Provides an uncategorized collection of possibly useful utilities.

:copyright: 2005-2007 Alan G. Isaac, except where another author is specified.
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
from __future__ import division
from __future__ import absolute_import

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '20070622'





def calc_gini2(x): #follow transformed formula
	'''Return computed Gini coefficient.

	:note: follows tranformed formula, like R code in 'ineq'
	:see: `calc_gini`
	:contact: aisaac AT american.edu
	'''
	x = list(x)
	n = len(x)
	x.sort()  # increasing order
	G = sum(x[i] * (i+1) for i in xrange(n))
	G = 2.0*G/(n*sum(x)) #2*B
	return G - 1 - (1./n)

def calc_gini(x):
	'''Return computed Gini coefficient.

	:note: follows basic formula
	:see: `calc_gini2`
	:contact: aisaac AT american.edu
	'''
	x = list(x)
	n = len(x)
	x.sort()  # increasing order
	G = sum( x[i] * (n-i) for i in xrange(n) )  #Bgross
	G = 2.0*G/(n*sum(x))
	return 1 + (1./n) - G


def permute(x):
	'''Return one permutation of a sequence or array.

	:since:  2005-06-20
	:date:   2007-06-22
	:contact: aisaac AT american.edu
	'''
	#use numpy if available
	try:
		x = numpy.array(x,copy=True)
		numpy.random.shuffle(x.flat)
	except:
		x = list(x) #1d only!
		random.shuffle(x)
	return x

def permutations(lst):
	'''Return all permutations of `lst`.
	
	:type lst:  sequence
	:rtype:     list of lists
	:return:    all permutations of `lst`
	:since:     2005-06-20
	:date:      2007-06-22
	:note:      recursive
	:contact: aisaac AT american.edu
	'''
	lst = list(lst)
	return [ [lst[i]] + x
					for i in range(len(lst))
					for x in permutations(lst[:i]+lst[i+1:])
	        ] or [[]]


def permutationsg(lst):
	'''Return generator of all permutations of a list.

	:type `lst`: sequence
	:rtype:      list of lists
	:return:     all permutations of `lst`
	:requires:   Python 2.4+
	:note:       recursive
	:since:      2005-06-20
	:date:       2006-12-18
	:see:        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465
	:contact:    mailto:aisaac AT american.edu
	'''
	if len(lst)>1:
		for i in range(len(lst)):
			for x in permutationsg(lst[:i]+lst[i+1:]):
				yield [lst[i]]+x
	else:
		yield lst

