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
__lastmodified__ = '20070922'

import logging, random, itertools

have_numpy = False
try:
	import numpy as N
	from numpy import linalg
	have_numpy = True
	logging.info("have_numpy is True")
except ImportError:
	logging.info("NumPy not available.")

have_scipy = False
if have_numpy:
	try:
		from numpy.distutils import cpuinfo
	except ImportError:
		logging.warn("numpy.distutils unavailable, cannot test for SSE2 -> SciPy disabled.")
		pass                  #safest to leave have_scipy = False
	else:
		#unfortunately some of scipy.stats expects sse2 and will segfault if absent!!
		cpu = cpuinfo.cpuinfo()
		if cpu._has_sse2():
			logging.info("SSE2 detected")
			try:
				from scipy import stats
				logging.info("successful import of scipy.stats as stats")
			except ImportError:
				logging.info("SciPy cannot be imported -> no probabilities computed.")
			else:
				have_scipy = True
				logging.info("have_scipy is True")
		else:
			logging.warn("Cannot detect SSE2; disabling SciPy")




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

def groupsof(seq,n):
	"""Return len(self)//n groups of n, discarding last len(self)%n players."""
	#use itertools to avoid creating unneeded lists
	return itertools.izip(*[iter(seq)]*n)


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

def combinations(n,t) :
	'''Return all t-combinations (as indices).

	:type `lst`: sequence
	:rtype:      list of lists
	:return:     all t-combinations of n elements (by index)
	:requires:   Python 2.4+ (for generators)
	:since:      2007-09-19
	:see:        Knuth vol.4 ch.3
	:author:     Charles Harris (using Knuth's algorithm)
	'''
	c = range(t + 2)  #use range not arange because it is faster and ...
	c[-2] = n
	c[-1] = 0
	while 1 :
		yield c[:t]  #... a slice of a list is a copy!
		j = 0
		while c[j] + 1 == c[j+1] :
			c[j] = j
			j += 1
		if j >= t :
			return
		c[j] += 1


###### set utilities ###########################################
#BEGIN subsetid
def subsetid(length):
	'''Return: binary representations of all subsets
	of a set of length `length`.
	'''
	if length==0:
		return ['']
	else:
		result0 = subsetid(length-1)
		return ['0'+id for id in result0]+['1'+id for id in result0]
#END subsetid

#:see: http://mail.python.org/pipermail/python-list/2001-May/085964.html
#BEGIN PowerSet
class PowerSet:
	'''
	All 2**n subsets are available by index in range(2**n).
	Binary representation of index is used for element selection.
	'''
	def __init__(self, s):
		'''
		:note: to know order ex ante, `s` shd be lst or tuple 
		'''
		self.s = s
		self.scard = len(s)  #cardinality of set s
		self.pscard = 2**self.scard #cardinality of powerset
	def __getitem__(self, idx):
		if idx < 0:
			idx += self.pscard
		if idx < 0 or idx >= self.pscard:
			raise IndexError("%i is out of range"%(i))
		result = set( si for i,si in enumerate(self.s) if (idx>>i)&1 )
		return result
#END PowerSet

#########  marginally relevant utilities  ######################
def int2binary(i, strlen=None, reverse=False):
	"""Return binary string representation of nonnegative integer.
	`i` is the integer.
	`strlen` is number of 'bits' in the representation.
	"""
	assert i>=0, "Nonnegative integers only"
	if strlen is None:
		strlen = 4  #set a minumu string length
		n = i>>4
		while n:
			n >>= 4
			strlen += 4
		strlen = max(1,strlen) #to handle 0
	else:
		assert i<2**strlen, "Inadequate string length."
	if reverse:
		result = "".join( str((i>>y)&1) for y in range(strlen) )
	else:
		result = "".join( str((i>>y)&1) for y in range(strlen-1, -1, -1) )
	return result

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


