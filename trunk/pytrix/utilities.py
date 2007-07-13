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

import random
try:
	import numpy
except ImportError:
	pass





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


def gini2shares(gini, nbrackets, shuffle=False):
	'''Return: income share for each bracket implied by `gini`.

	:note: based on Yunker 1999, p.238
	:todo: improve computation accuracy
	:note: consider Lorenz curve function representation
	       y=x**g for 0<g<1.
	       B = \int_0^1 x**g dx = x**(g+1)/(g+1) | = 1/(g+1)
	       So G = 1-2B = (g-1)/(g+1)
	       Note (1+G)/(1-G) = 2g/2 = g. (Used below.)
	:since:  2006-06-20
	:date:   2007-07-11
	:contact: aisaac AT american.edu
	'''
	assert (0 <= gini < 1)
	g = (1+gini)/(1-gini) # (2A+B)/B
	sb = 1.0/nbrackets  #width of brackets
	#cum prop =  ((i+1)*sb)**g = (i+1)**g * sb**g
	#change prop = [(1+i)**g-(i)**g]*sb**g
	#cumulative_proportions = list( ((i+1)*sb)**g for i in range(nbrackets) )
	shares = [ ((1+i)**g-(i)**g)*sb**g for i in range(nbrackets)]  #chk TODO
	if shuffle:   #enforce Gini but distribute randomly
		random.shuffle(shares)
	return shares


def n_each_rand(n,itemtuple=(True,False)):
	'''Yield: n of each of two items,
	one at a time, in random order.

	:since:  2006-06-20
	:date:   2007-07-11
	:contact: aisaac AT american.edu
	'''
	item0, item1 = itemtuple
	ct0, ct1 = 0, 0
	while ct0+ct1<2*n:
		if random.random() < ((n-ct0)/(2.0*n-ct0-ct1)):
			next_item = item0
			ct0 += 1
		else:
			next_item = item1
			ct1 += 1
		yield next_item


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
	except NameError:
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



#########  marginally relevant utilities  ######################
def grep(pattern, *files):
	'''Usage: grep("grep", *glob.glob("*.py"))

	:author: Fredrik Lundh
	:since: 2005-10-25
	'''
	try:
		search = re.compile(pattern).search
	except NameError:
		import re
		search = re.compile(pattern).search
	for file in files:
		for index, line in enumerate(open(file)):
			if search(line):
				print ":".join((file, str(index+1), line[:-1]))


