'''
Provides an uncategorized collection of possibly useful utilities.
'''
from __future__ import division
from __future__ import absolute_import

def calc_gini2(x): #follow transformed formula
	'''Return computed Gini coefficient.
	:note: follows tranformed formula, like R code in 'ineq'
	:see: `calc_gini`
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
	'''
	x = list(x)
	n = len(x)
	x.sort()  # increasing order
	G = sum( x[i] * (n-i) for i in xrange(n) )  #Bgross
	G = 2.0*G/(n*sum(x))
	return 1 + (1./n) - G


def permute(x):
	'''Return one permutation of a sequence or array.

	:author: Alan Isaac
	:since:  2005-06-20
	:date:   2006-11-22
	'''
	if have_numpy:
		x = numpy.array(x,copy=True)
		numpy.random.shuffle(x.flat)
	else:
		x = list(x) #1d only!
		random.shuffle(x)
	return x

def permutations(lst):
	'''Return all permutations of `lst`.
	
	:type lst:  sequence
	:rtype:     list of lists
	:return:    all permutations of `lst`
	:since:     2005-06-20
	:note:    recursive
	:contact:   mailto:aisaac AT american.edu
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
	:author:     Alan G. Isaac
	:contact:    mailto:aisaac AT american.edu
	:see:        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465
	'''
	if len(lst)>1:
		for i in range(len(lst)):
			for x in permutationsg(lst[:i]+lst[i+1:]):
				yield [lst[i]]+x
	else:
		yield lst

